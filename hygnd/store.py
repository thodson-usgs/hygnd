import pandas as pd
from hygnd.stream.nwis import get_records
from hygnd.munge import interp_to_freq, fill_iv_w_dv, filter_param_cd
from hygnd.utils.analysis.said import format_constituent_df, format_surrogate_df
from hygnd.datasets.codes import pn #XXX need to move this into site var
import numpy as np

SERVICES = ['iv','dv','qwdata','site']

class SAIDStore(pd.HDFStore):
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
        iv = filter_param_cd(iv, 'A').replace(-999999, np.NaN)
        dv = filter_param_cd(dv, 'A').replace(-999999, np.NaN)
        iv = interp_to_freq(iv, freq=15, interp_limit=120)
        
        if '00060' in iv.columns:
            iv = fill_iv_w_dv(iv, dv, freq='15min', col='00060')
        
        if '51289' in iv.columns:
            iv['51289'] = interp_to_freq(iv['51289'], freq=15,
                                        interp_limit=10000)
        
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
            
    def test(self):
        print('test')
        
        
class NWISStore(pd.HDFStore):
    """class works on pytables hdf
    
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
            if type(df) != type(None):
            #df.reset_index(level=0, inplace=True)
                group = 'site/{}/{}'.format(site,service)
                self.put(group, df, format='fixed')
        
        #update metadata with time of download
        #meta should also include huc and state for grabbing sites
        
        #see ptrepack for better compression
        #complevel=9, complib='blosc:blosclz'
        
    def _update_recent(self, sites):
        """A simple update function
        Only gets data since the last punch in the db. Doesn't check if older data
        was updated
        """
        if type(sites) == 'list':
            for site in sites:
                self._update_recent(site)
        else:
            site = sites #only one site
            for service in ['iv','dv','qwdata']:
                
                #print('{} {}'.format(site,service))
                group = '/site/{}/{}'.format(site,service)
                
                if group not in self.keys():
                    break
                    
                old_df = self.get(group)
                last_time = old_df.iloc[-1].name.strftime('%Y-%m-%d')
                new_df = get_records(site, start=last_time, end=None)
                updates = new_df.index.intersection(old_df.index)
                updated = old_df.append(new_df.loc[updates])
                
                self.put(group, updated, format='fixed')
            
            
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
            
        
    def update(self, group):
        self.get(group)
        pass
    

    #add_site
    
    #bootstrap
    
    #update method
    
    #