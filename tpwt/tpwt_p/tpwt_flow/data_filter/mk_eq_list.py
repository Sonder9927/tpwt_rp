from concurrent.futures import ThreadPoolExecutor
from icecream import ic
from threading import Lock
from pathlib import Path

from tpwt_p.check import check_exists
from tpwt_p.rose import glob_patterns


def mk_eqlistper(p, evts, stas) -> Path:
    events = find_events(evts, p.data)
    stations = find_stations(stas, p.region)
    get_eqlistper(p, events, stations)
    return eqlistper


###############################################################################


def find_events(evts, dir: Path) -> list:
    """
    Return a list of events
    that are in both file_name and dir_name.
    """
    s = lambda x: [str(i) for i in x]

    e1 = s(evts)
    e2 = s(glob_patterns("glob", dir, ["**"]))
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

    
##############################################################################


def process_events_tempper(p, events, stas) -> dict:
    temppers = {}

    # need a lock for the dict temppers
    lock = Lock()

    def process_event_tempper(evt: str):
        """
        batch function
        """
        filelist = check_exists(p.data / evt / 'filelist')
        with open(filelist, 'r') as f:
            sacs = f.read().splitlines()

        tempper = [i for sta in stas if (i := f'{evt}.{sta}.LHZ.sac') in sacs]

        if len(tempper) <= p.nsta:
            ic(evt, "not enough stations")
        else:
            lock.acquire()
            temppers[evt] = tempper
            lock.release()

        ic(evt, "done")

    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.submit(process_event_tempper, events)

    return temppers


##############################################################################


def write_events_eqlistper(sac_dir, temppers: dict):
    eqlistper = sac_dir / 'eqlistper'
    # need a lock for the file eqlistper
    lock = Lock()

    # first line
    with open(eqlistper, 'w') as f:
        f.write(f'{len(temppers)}\n')

    def write_event_eqlistper(evt, evt_id):
        """
        batch function
        get content for write into file eqlistper
        the first line for every valid event is
        total number of sac files exists, evt_num
        """
        content = f'    {len(temppers[evt])} {evt_id}\n'

        # sac files' position will follow it
        evt_dir = sac_dir / evt
        for sac in temppers[evt]:
            content += f'{evt_dir/sac}\n'

        # write content into file
        lock.acquire()
        with open(eqlistper, 'a') as f:
            f.write(content)
        lock.release()

    evt_list = sorted([*temppers])
    with ThreadPoolExecutor(max_workers=5) as pool:
        pool.map(write_event_eqlistper, evt_list, [i+1 for i in range(len(evt_list))])


def get_eqlistper(p, events, stations):
    # process every event
    # find valid events
    temppers = process_events_tempper(p, events, stations)
    
    # write eqlistper
    write_events_eqlistper(p.data, temppers)
