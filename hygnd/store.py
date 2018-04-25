import pandas as pd
from hygnd.stream.nwis import get_records
from hygnd.munge import interp_to_freq, fill_iv_w_dv, filter_param_cd
from hygnd.utils.analysis.said import format_constituent_df, format_surrogate_df
from hygnd.datasets.codes import pn #XXX need to move this into site var
import numpy as np

SERVICES = ['iv','dv','qwdata','site']

"""
define NWIS codes
https://waterdata.usgs.gov/nwis?codes_help
"""
#NWIS dv and iv codes
# ---------------------------------
# Code   Description
# ---------------------------------
# Ssn    Parameter monitored seasonally
# Bkw    Flow affected by backwater
# Ice    Ice affected
# Pr     Partial-record site
# Rat    Rating being developed or revised
# Eqp    Equipment malfunction
# Fld    Flood damage
# Dry    Dry
# Dis    Data-collection discontinued
# --     Parameter not determined
# Mnt    Maintenance in progress
# ZFl    Zero flow
# ***    Temporarily unavailable
NWIS_codes = [
    'A',   # Approved
    'Ssn', # Parameter monitored seasonally
    'Bkw', # Flow affected by backwater
    'Ice', # Ice affected
    'Pr',  # Partial-record site
    'Rat', # Rating being developed or revised
    'Eqp', # Equipment malfunction
    'Fld', # Flood damage
    'Dry', # Dry
    'Dis', # Data-collection discontinued
    '--',  # Parameter not determined
    'Mnt', # Maintenance in progress
    'Zfl', # Zero flow
    '***'  # Temporarily unavailable
]

flag = {code:i**2 for i,code in enumerate(NWIS_codes)}


class HGStore(pd.HDFStore):
    """
    """
    def stations(self):
        """Returns a list of stations within store
        """
        stations = []
        keys = self.keys()

        paths = [s for s in keys if "site" in s]

        stations = [ s.split('/')[2] for s in paths]

        return list(set(stations))


    #def get(self, key):
    #    df = super().get(key)
    #    return df
    #    #return df.replace(-999999, np.NaN)

    #def put(self, group, df, format='fixed'):
    #    #out = df.replace(np.NaN, -999999, inplace=True)
    #    out = df
    #    super().put(group, out, format='fixed')

class SAIDStore(HGStore):
    def _prep_site(self, site, verbose=True):
        """Prepare and store dataframes for input to SAID
        """
        if verbose:
            print(site)
        dv = self.get(key='site/{}/dv'.format(site))
        iv = self.get(key='site/{}/iv'.format(site))

        qw_key = '/site/{}/qwdata'.format(site)

        if qw_key in self.keys():
            qwdata = self.get(key=qw_key)
            qwdata = format_constituent_df(qwdata)
            self.put('site/{}/said/qwdata'.format(site), qwdata)
        #TODO remove samples too close in time

        #clean iv
        #XXX review this
        iv = iv.replace('P,e','A').replace('P:e','A')

        iv = filter_param_cd(iv, 'A')#.replace(-999999, np.NaN)
        dv = filter_param_cd(dv, 'A')#.replace(-999999, np.NaN)
        iv = interp_to_freq(iv, freq=15, interp_limit=120)

        if '00060' in iv.columns:
            iv = fill_iv_w_dv(iv, dv, freq='15min', col='00060')

        if '51289' in iv.columns:
            iv['51289'] = interp_to_freq(iv['51289'], freq=15,
                                        interp_limit=480)

        iv = format_surrogate_df(iv)

        #drop rows with only discharge
        #check_cols = iv.columns.drop('Discharge')
        #iv.dropna(how='all', subset=check_cols)
        #for i in [iv, qwdata]:
            # I *believe* SAID only works on single layer index, 
            # so strip site_no from index
         #   i.reset_index(level=0, inplace=True)

        self.put('site/{}/said/iv'.format(site), iv)

    def _apply_proxy(self, dst_id, src_id, field):
        field = pn[field] #translate to SAID XXX
        dst_df = self.get(key='site/{}/said/iv'.format(dst_id))
        src_df = self.get(key='site/{}/said/iv'.format(src_id))

        dst_df[field] = np.NaN
        dst_df.update(src_df[[field]])

        self.put('site/{}/said/iv'.format(dst_id), dst_df)

    def _prep_sites(self,sites):
        """
        Args:
            sites (list): list of dicts, each containing an id field
        """
        for site in sites:
            self._prep_site(site['id'])

        for site in sites:
            proxies = site.get('proxies')
            if proxies:
                for proxy in proxies:
                    dst_id = site['id']
                    src_id = proxies[proxy] #confusing, returns site name
                    self._apply_proxy(dst_id, src_id, proxy)


class NWISStore(HGStore):
    """class works on pytables hdf

    """
    #open
    #init pass filename
    #set for HDFStore(file, complevel=9, complib='blosc:blosclz)'
    #alternatively better compression may be achieved with ptrepack
    #wrapper 

    #add more services
    #should go in a hygndstore XXX testing

    def _download_site(self, site, start=None, end=None, service='all'):

        if service =='all':
            for service in SERVICES:
                self._download_site(site, start=start, end=end,
                               service=service)
        #elif list for service in list loop
        else:
            df = get_records(site, start=start, end=end, 
                             service=service)
            if type(df) != type(None):
            #df.reset_index(level=0, inplace=True)
                group = 'site/{}/{}'.format(site,service)
                self.put(group, df, format='fixed')

        #update metadata with time of download
        #meta should also include huc and state for grabbing sites

        #see ptrepack for better compression
        #complevel=9, complib='blosc:blosclz'


    def get_station(station_id):
        return Station(site['id'], self._path)


    def spinup(self, project_template):
        """Download data for all stations specified in project

        Parameters
        ----------
        project_template : dict
            dictionary specifying the organization of stations within the project

        TODO: add check to make sure hdf does not already exist
        """
        p = Project(project_template)

        services = p.station_services()

        for site in p.stations(proxies=True):

            if verbose:
                print(site)

            station = self.get_station(site['id'])

            for service in p.services:
                station.download(service, start=site['start'])


    def _spinup_sites(self, sites, service='all', verbose=True):
        """
        Args:
            sites (list): list of site numbers to include in hdf
            see super_network example
        """
        for site in sites:

            if verbose:
                print(site)
            self._download_site(site['id'], start=site['start'], service=service)



    def update(self, station_id=None, service=None):
        """Update station object in datastore.

        TODO: add approval parameter
        """

        if all([station_id, service]):
            station = self.get_station(Station(station_id, self._path)
            station.update(service)

        elif station_id:
            station = Station(station_id, self._path)
            station.update()

        else:
            station_ids = self.stations()
            for station_id in station_ids:
                station = Station(station_id, self._path)
                station.update()
                #get existing services

