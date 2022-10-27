from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
from collections import namedtuple
from pathlib import Path
from icecream import ic
from tqdm import tqdm
import os
import obspy
import subprocess

from tpwt_p import rose


Param_Z = namedtuple("Param_Z", "target_z zfile")

Param_cut = namedtuple("Param_cut", "id sacs mktraceiodb cutevent cat time_delta target_cut")


class Evt_Cut:
    def __init__(self, data: str) -> None:
        self.data = Path(data)
        ic("Hello, this is EVT cutter.")

    def get_Z_1Hz(self, target: str, patterns: list):
        """
        from data get only Z component sac files and downsample to 1 Hz 
        will put into `target` dir
        cut by catalogue created by two csv files
        """
        ic("getting only_Z_1Hz...")

        self.target_z = Path(target)
        self.patterns = patterns

        # clear and re-create
        self.target_z = rose.re_create_dir(target)

        zfiles = rose.glob_patterns("rglob", self.data, patterns)

        ps = [(Param_Z(self.target_z, z)) for z in zfiles]

        # Pool(10).map(batch_1Hz, ps)
        for _ in tqdm(Pool(10).imap(batch_1Hz, ps)):
            pass

    def cut_event(self, target, cat, time_delta, cut_from=None, patterns=[]):
        """
        cut event from only_Z_1Hz using event.cat
        and result is in cut_dir
        """
        ic("getting cutted events...")
        if cut_from:
            cut_from = Path(cut_from)
        else:
            cut_from = self.target_z
            patterns = self.patterns

        self.target_cut = rose.re_create_dir(target)

        # get binary program
        mktraceiodb = rose.get_binuse('mktraceiodb')
        cutevent = rose.get_binuse('cutevent')

        # get list of mseed/SAC files (direcroty and file names)
        sacs = rose.glob_patterns("rglob", cut_from, patterns)
        # batch process
        batch = 1_000
        sacs_batch_list = [sacs[i: i+batch] for i in range(0, len(sacs), batch)]

        ps = [
            Param_cut(
                i+1, s, mktraceiodb, cutevent, cat, time_delta, self.target_cut
            ) for i, s in enumerate(sacs_batch_list)
        ]

        # Pool(10).map(batch_1Hz, ps)
        Pool(10).map(batch_cut_event, ps)


# batch function
###############################################################################


def batch_1Hz(p: Param_Z):
    """
    batch function for get_Z_1Hz 
    to down sample every target file
    which will be putted into z_dir
    """
    file_z = p.target_z / p.zfile.name
    # decimate_sac(p.zfile, file_z)
    decimate_obspy(p.zfile, str(file_z))


def batch_cut_event(p: Param_cut):
    """
    batch function for cut_event 
    """
    lst = f"data_z.lst_{p.id}"
    db = f"data_z.db_{p.id}"
    done_lst = f"done_z.lst_{p.id}"

    with open(lst, "w+") as f:
        for sac in p.sacs:
            f.write(f"{sac}\n")

    ic(p.id)
    cmd_string = 'echo shell start\n'
    cmd_string += f'{p.mktraceiodb} -L {done_lst} -O {db} -LIST {lst} -V\n'  # no space at end!
    cmd_string += f'{p.cutevent} '
    cmd_string += f'-V -ctlg {p.cat} -tbl {db} -b +0 -e +{p.time_delta} -out {p.target_cut}\n'
    cmd_string += 'echo shell end'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())

    rose.remove_targets([lst, db, done_lst])


###############################################################################


def decimate_sac(ffrom, fto):
    # method by sac
    s = f"r {ffrom} \n"
    s += "decimate 5 \n"
    s += f"w {fto} \n"
    s += "q \n"
    os.putenv("SAC_DISPLAY_COPYRIGHT", "0")
    subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())


def decimate_obspy(ffrom, fto: str):
    # method by obspy
    # Read the seismogram.
    st = obspy.read(ffrom)
    # There is only one trace in Stream object.
    tr = st[0]
    # Decimate 5Hz by a factor of 5 to 1Hz.
    # Note that this automatically includes a lowpass filtering with corner frequency 20Hz.
    tr_new = tr.copy()
    tr_new.decimate(factor=5, strict_length=False)
    # Save the new data.
    tr_new.write(fto, format="SAC")
