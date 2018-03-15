from usgs_tools.portals import nwis
from pandas import HDFStore, DataFrame


class GaugeNetwork:
    
    def put(self, group, df):
        sites = df.index.levels[0]
        key = '{}/{}'.format(group,name)
        hdf = HDFStore(self._filename)
        hdf.put()
        
    
    def load(self, filename):
        pass
        
    
    def save(self, filename):
        pass
        
    
    def update(self, filename):
        pass
        #get list of records and 
        #get list of samples
        
    def bootstrap_records(filename, sites, start_year):
        self._filename = filename
        hdf = HDFStore(filename)
        
        start = '{}-01-01'.format(start_year)
        end   = '{}-12-31'.format(start_year)
        
        df = get_record(sites, start=start, end=end)
        hdf.put('records', df,format='table', data_columns=True)

        for site in sites[1:]:
            df = get_record(site)
            hdf.append('records', df, format='table', data_columns=True)
            
            
            
    
            
    
