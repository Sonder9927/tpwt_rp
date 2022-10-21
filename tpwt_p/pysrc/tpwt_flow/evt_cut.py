from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from icecream import ic
import os, shutil
import subprocess

from pysrc.tpwt import get_binuse

class Evt_Cut:
    def __init__(self, data, patterns, z) -> None:
        self.data = Path(data)
        self.patterns = patterns
        self.z = z

    def get_Z_1Hz(self, target):
        """
        from data get only Z component sac files and downsample to 1 Hz 
        will put into `target` dir
        cut by catalogue created by two csv files
        """
        ic("getting only_Z_1Hz...")

        self.target_z = Path(target)
        # clear and re-create
        if self.target_z.exists():
            shutil.rmtree(self.target_z)
        self.target_z.mkdir(parents=True)

        files_lst = []
        for pattern in self.patterns:
            files_lst += list(self.data.rglob(pattern))

        def batch_1Hz(file_path):
            """
            batch function for get_Z_1Hz 
            to down sample every target file
            which will be putted into z_dir
            """
            file_z = self.target_z / f"{file_path.name}_{self.z}"

            s = f"r {file_path} \n"
            s += "decimate 5 \n"
            s += f"w {file_z} \n"
            s += "q \n"
            os.putenv("SAC_DISPLAY_COPYRIGHT", "0")
            subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())

        with ThreadPoolExecutor(max_workers=4) as pool:
            pool.map(batch_1Hz, files_lst)

    def cut_event(self, target, cat, cut_from=None, pattern=None):
        """
        cut event from only_Z_1Hz using event.cat
        and result is in cut_dir
        """
        ic("getting cutted events...")
        if cut_from:
            cut_from = Path(cut_from)
        else:
            cut_from = self.target_z
            pattern = f"*_{self.z}"

        target_cut = Path(target)
        if target_cut.exists():
            shutil.rmtree(target_cut)
        target_cut.mkdir(parents=True)

        # get list of mseed/SAC files (direcroty and file names)
        sacs = list(cut_from.rglob(pattern))
        # batch process
        batch = 1_000
        sacs_batch_list = [sacs[i: i+batch] for i in range(0, len(sacs), batch)]

        # batch function for cut_event 
        def batch_cut_event(sacs: list, id: int):
            ic(id)
            lst = f"data_z.lst_{id}"
            db = f"data_z.db_{id}"
            done_lst = f"done_z.lst_{id}"

            with open(lst, "w+") as f:
                for sac in sacs:
                    f.write(f"{sac}\n")

            mktraceiodb = get_binuse('mktraceiodb')
            cutevent = get_binuse('cutevent')

            cmd_string = 'echo shell start\n'
            cmd_string += f'{mktraceiodb} -L {done_lst} -O {db} -LIST {lst} -V\n'  # no space at end!
            cmd_string += f'{cutevent} '
            cmd_string += f'-V -ctlg {cat} -tbl {db} -b +0 -e +10800 -out {target_cut}\n'
            cmd_string += 'echo shell end'
            subprocess.Popen(
                ['bash'],
                stdin = subprocess.PIPE
            ).communicate(cmd_string.encode())

            for file in [lst, db, done_lst]:
                os.remove(file)

        with ThreadPoolExecutor(max_workers=5) as pool:
            pool.map(
                batch_cut_event,
                sacs_batch_list,
                [i for i in range(len(sacs_batch_list))]
            )
