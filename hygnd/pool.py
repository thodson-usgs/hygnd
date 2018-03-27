import pandas as pd
from hygnd.stream.nwis import get_records

SERVICES = ['iv','dv','qwdata','site']
                
class NWISStore(pd.HDFStore):
    """class works on pytables hdf
    
    
    example  structure
    /
    gage, well, watershed
    """
    #open
    #init pass filename
    #set for HDFStore(file, complevel=9, complib='blosc:blosclz)'
    #alternatively better compression may be achieved with ptrepack
    #wrapper 
    
    #add more services
    def _download_site(self, site, start=None, end=None, service='all'):
        
        if service =='all':
            for service in SERVICES:
                self._download_site(site, start=start, end=end,
                               service=service)
        #elif list for service in list loop
        else:
            df = get_records(site, start=start, end=end, 
                             service=service)
            df.reset_index(level=0, inplace=True)
            group = 'site/{}/{}'.format(site,service)
            self.put(group, df, format='fixed')
        
        #update metadata with time of download
        #meta should also include huc and state for grabbing sites
        
        #see ptrepack for better compression
        #complevel=9, complib='blosc:blosclz'
        
    def _spinup_sites(self, sites, start=None, service='all'):
        """
        Args:
            sites (list): list of site numbers to include in hdf
        """
        for site in sites:
            self._download_site(site, start=start, service=service)
    
    def update(self, group):
        self.get(group)
        pass
    

    #add_site
    
    #bootstrap
    
    #update method
    
    #