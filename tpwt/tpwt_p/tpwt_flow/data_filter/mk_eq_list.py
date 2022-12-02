from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from collections import namedtuple
from icecream import ic
from threading import Lock
from pathlib import Path

from tpwt_p.check import check_exists
from tpwt_p.rose import glob_patterns


Param_tem = namedtuple("Parma_tem", "data stas evt nsta lock")
Param_we = namedtuple("Parma_tem", "sac_dir evt_id evt temppers")


def mk_eqlistper(p, evts, stas) -> Path:
    events = find_events(evts, p.data)
    stations = find_stations(stas, p.region)

    # process every event
    # find valid events
    temppers = process_events_tempper(p, events, stations)
    
    # write eqlistper
    eqlistper = write_events_eqlistper(p.data, temppers)
    return eqlistper


###############################################################################


def process_events_tempper(p, events, stas) -> dict:
    temppers = {}

    # need a lock for the dict temppers
    lock = Lock()

    ps = [Param_tem(p.data, stas, e, p.nsta, lock) for e in events]

    temppers = {}
    for tem in Pool(10).imap(process_event_tempper, ps):
        if tem:
            temppers.update(tem)
    return temppers

def write_events_eqlistper(sac_dir, temppers: dict):
    eqlistper = sac_dir / 'eqlistper'

    f = open(eqlistper, 'w+')
    # first line
    f.write(f'{len(temppers)}\n')

    evt_list = sorted([*temppers])

    ps = [Param_we(sac_dir, i+1, e, temppers) for i, e in enumerate(evt_list)]

    for content in Pool(10).imap(write_event_eqlistper, ps):
        if content:
            f.write(content)

    f.close()
    return eqlistper


##############################################################################
"""
batch function
"""


def process_event_tempper(p):
    """
    batch function
    """
    filelist = check_exists(p.data / p.evt / 'filelist')

    with open(filelist, 'r') as f:
        sacs = f.read().splitlines()

    tempper = [i for sta in p.stas if (i := f'{p.evt}.{sta}.LHZ.sac') in sacs]

    if len(tempper) <= p.nsta:
        ic(p.evt, "not enough stations")
        return False
    else:
        # ic(evt, "done")
        return {p.evt: tempper}


def write_event_eqlistper(p: Param_we):
    """
    batch function
    get content for write into file eqlistper
    the first line for every valid event is
    total number of sac files exists, evt_num
    """
    tems_evt = p.temppers[p.evt]
    content = f'    {len(tems_evt)} {p.evt_id}\n'

    # sac files' position will follow it
    evt_dir = p.sac_dir / p.evt
    for sac in tems_evt:
        content += f'{evt_dir/sac}\n'

    return content


##############################################################################


def find_events(evts, sac_dir: Path) -> list:
    """
    Return a list of events
    that are in both file_name and dir_name.
    """
    s = lambda x: [str(i) for i in x]

    e1 = s(evts)
    e2 = s(glob_patterns("glob", sac_dir, ["20*"]))
    return e1|e2


def find_stations(stas, area):
    """
    Return a list of stations in the sta_file
    that are in the area.
    """
    sta_in_area = stas[
        (stas.la >= area.sourth)
        & (stas.la <= area.north)
        & (stas.lo >= area.west)
        & (stas.lo <= area.east)
    ]

    return [i for i in sta_in_area['sta']]
