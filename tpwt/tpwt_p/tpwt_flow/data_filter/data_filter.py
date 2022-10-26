from pathlib import Path

from tpwt_p.rose import read_xyz

from .calculate import calculate_dispersion
from .aftan_snr import process_events_aftan_snr
from .sta_dist import process_periods_sta_dist
from .mk_eq_list import mk_eqlistper

class Data_Filter:
    def __init__(self, bp, periods: list) -> None:
        self.bp = bp
        self.evts = read_xyz(self.bp.evt, ['sta', 'lo', 'la'])
        self.stas = read_xyz(self.bp.sta, ['sta', 'lo', 'la'])
        self.periods = periods

    def calculate_dispersion(self, path, disp_list=[]):
        """
        genetate inter-station dispersion curves using the GDM model.
        """
        calculate_dispersion(sta_v2(self.evts), sta_v2(self.stas), path, disp_list)
        self.path = path
        return "Flag GDM52 done."

    def aftan_snr(self, path):
        try:
            self.path
        except AttributeError:
            self.calculate_dispersion(path)
        finally:
            process_events_aftan_snr(self.bp.data, self.path, self.bp.work_dir)

        return "Flag aftan_snr done."

    def sta_dist(self, snr, tcut):
        # set snr and tcut
        self.bp.set_snr_tcut(snr, tcut)
        process_periods_sta_dist(self.bp, self.periods, self.bp.work_dir)

    def mk_eqlistper(self):
        self.eq_list = mk_eqlistper(self.bp, self.evts["sta"], self.stas)

    def eqlistper(self):
        try: 
            self.eq_list
        except AttributeError:
            self.mk_eqlistper()

        return self.eq_list
        

def sta_v2(sta):
    sta[['lo', 'la']] = sta[['la', 'lo']]
    return sta
