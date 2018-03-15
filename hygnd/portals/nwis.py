import pandas as pd
import requests
from io import StringIO
import numpy as np
import re

NWIS_URL = 'https://waterservices.usgs.gov/nwis/iv/'
QWDATA_URL =  'https://nwis.waterdata.usgs.gov/nwis/qwdata?'

code_lookup = {
    'discharge':'00060',
    'temperature':'00010',
    'nitrate':'99133',
    'turbidity':'63680'
}
###############################################################################
def rdb_to_df(url, params=None):
    """ Get rdb table and return dataframe
    
    Args:
          url (string): Base url 
          params: Parameters for REST request
          
    See https://waterdata.usgs.gov/nwis?automated_retrieval_info
    """
    req = requests.get(url, params=params)
    #XXX
    count = 0
    
    #print(req.url)
    rdb = req.text
    for line in rdb.splitlines():
        # ignore comment lines
        if line.startswith('#'):
            count = count + 1
        
        else:
            break
    
    fields = rdb.splitlines()[count].split('\t')
    dtypes = {'site_no': str}
    #dtypes =  {‘site_no’: str, }
    df = pd.read_csv(StringIO(rdb), delimiter='\t', skiprows=count+2, names=fields,
                     na_values='NaN', dtype=dtypes)
        
    return df 

###############################################################################
def get_record(sites, start=None, end=None, param_cds=None, *args):
    """Pull hydrographic records from NWIS and return as dataframe.

    Uses requests and rdb_to_df to request and format an rdb timeseries from NWIS
    
    Args:
        site (string): X digit USGS site ID. 05586300
        start: 2018-01-25
        end:
        args: list of data fields

    Returns:
        Return an object containing the gage record
        
    """ 
    #sites = to_str(sites)
    
    df = pd.DataFrame()
    payload = {'format':'rdb' } 
    
    if start: payload['startDT'] = start
    if end:   payload['endDT']   = end
        
    if param_cds: 
        payload['parameterCd'] = to_str(param_cds)
   
    #XXX Temp
    payload['sites'] = sites
    df = rdb_to_df(NWIS_URL, payload)
    return df
    #df['datetime'] = pd.to_datetime(df['datetime'])  
    #
    #if type(sites) == str: 
    #    sites = [sites]  
    #    for site in sites: 
    #        payload['sites'] = site
    #    temp_df = rdb_to_df(NWIS_URL, payload)
    #    temp_df['datetime'] = pd.to_datetime(df['datetime'])
    #df.set_index(['site_no','datetime'], inplace=True)
    
    return df 
#####
#XXX: I think we can delete this one 3/12/18
def foo(df):
    """Take an rdb and reformat column names
    """
    columns = df.columns.tolist()
    index     = columns[:4]
    param_cds = [i[6:] for i in param_cds[4:]]
    
    ###XXX BAD
    for cd in param_cds:
        if param_cds.count(cd) > 1: #if code occurs more than once
            indices = [j for j, x in enumerate(test) if x == i]
            test[indices[1]] = test[indices[1]] +'_b'
            
###############################################################################
def to_str(listlike):
    """
    XXX Move this to core module 
    """
    if type(listlike) == list:
        return ','.join(listlike)
    
    elif type(listlike) == pd.core.series.Series:
        return ','.join(listlike.tolist())
        
    elif type(listlike) == str:
        return listlike
    
###############################################################################
def get_samples(sites=None, state_cd=None,
                  start=None, end=None, *args):
    """Pull water quality sample data from NWIS and return as dataframe.
    
    Args:
      site (string): X digit USGS site ID. USGS-05586300
      start: 2018-01-25
      end:
    """
    #payload = {'sites':siteid, 'startDateLo':start, 'startDateHi':end, 
    #       'mimeType':'csv'} 
    
        
    payload = {'agency_cd':'USGS', 'format':'rdb', 
               'pm_cd_compare':'Greater than', 'inventory_output':'0',
               'rdb_inventory_output':'file', 'TZoutput':'0',
               'radio_parm_cds':'all_parm_cds', 'rdb_qw_attributes':'expanded',
               'date_format':'YYYY-MM-DD', 'rdb_compression':'value',
               'submmitted_form':'brief_list', 'qw_sample_wide':'separated_wide'}
    
    # check for sites and state_cd, and if list-like, convert them to strings/freq
    
    if sites:
        payload['site_no'] = to_str(sites)
    
    elif state_cd:
        payload['state_cd'] = to_str(state_cd)
        
    else:
        raise ValueError('Site or state must be defined')
    
    if start: payload['begin_date'] = start
    
    if end: payload['end_date'] = end
        
    df = rdb_to_df(QWDATA_URL, payload) 
    df['datetime'] = pd.to_datetime(df.pop('sample_dt') + ' ' +
                                    df.pop('sample_tm'),
                                    format = '%Y-%m-%d %H:%M')
    #df.set_index(['site_no','datetime'], inplace=True)
    
    return df 

def site_desc(sites):
    """
    Get site description information from NWIS
    """
    
    url = 'https://waterservices.usgs.gov/nwis/site/?'
    
    sites = to_str(sites) 
    payload = {'sites':sites, 'format':'rdb'}
    
    df = rdb_to_df(url, payload)
    #df.set_index(['site_no'], inplace=True)
    return df


def param_cds():
    """
    """
 
    url = 'https://nwis.waterdata.usgs.gov/nwis/pmcodes?radio_pm_search=param_group&pm_group=All+--+include+all+parameter+groups&pm_search=&casrn_search=&srsname_search=&format=rdb&show=parameter_group_nm&show=parameter_nm&show=casrn&show=srsname&show=parameter_units'
    
    df = rdb_to_df(url)
    #df.set_index(['parameter_cd'], inplace=True)
    
    return df
###############################################################################

#XXX
def get_records(sites, start, end, *args):
    """
    Args:
    
    Return:
    """
    json = get_gage_json(sites, start, end, *args)
    record_df = parse_gage_json(json)
    
    return record_df

def sample_gage_record():
    
    return get_gage_json('05586300','2016-10-1','2017-9-30','nitrate','temperature')

def get_gage_json(sites, start=None, end=None, params=None, freq=None, *args, **kwargs):
    """Function to get gage data

    Args:
        site (string): X digit USGS site ID. 05586300
        start: 2018-01-25
        end:
        kwargs: any additional parameter codes, namely 'parameterCD'

    Returns:
        Return an object containing the gage record
        
    
    See https://waterdata.usgs.gov/nwis?automated_retrieval_info

    """ 
    
    url = 'https://waterservices.usgs.gov/nwis/iv/'
    
    # if daily values were requested
    if freq=='dv':
        url = re.sub('iv/$','dv/$', url)
    
    sites = to_str(sites)
    
    payload = {'sites':sites, 'startDT':start, 'endDT':end, 
               'format':'json'} #, 'parameterCD':''} 
    
    if start:
        payload['startDT'] = start
    if end:
        payload['endDT'] = end
    
    if params:
        payload['parameterCD'] = to_str(params)
        
    #for arg in kwargs:
    #    payload[arg]=to_str(kwargs[arg]) 
    
   
    req = requests.get(url, params=payload)
    req.raise_for_status()
    print(req.url)
    return req.json()


def parse_gage_json(json):
    """Parses an NWIS json into a pandas DataFrame
    
    Args:
        json (dict)
    
    """
    
    df = pd.DataFrame( columns=['datetime','site_no'] )
    #import ipdb; ipdb.set_trace()
    for timeseries in json['value']['timeSeries']:
        #get site_no associated with timeseries
        site_no = timeseries['sourceInfo']['siteCode'][0]['value']
        param_cd = timeseries['variable']['variableCode'][0]['value']
       
        # loop through each parameter in timeseries. This is mainly relevant to turbidity
        for parameter in timeseries['values']:
            col_name = param_cd
            
            if len(timeseries['values']) > 1:
                   col_name = col_name + parameter['method'][0]['methodDescription']
            
            col_cd_name = col_name + '_cd'
            record_json = parameter['value']  
            
            if not record_json:
                #no data in record
                continue
                
            record_json = str(record_json).replace("'",'"')
            # read json, converting all values to float64 and all qaulifiers
            # to str. Lists can't be hashed, thus we cannot df.merge on a list column
            record_df   = pd.read_json(record_json, orient='records',
                                       dtype={'value':'float64',
                                              'qualifiers':'unicode'})
            
            record_df['qualifiers'] = record_df['qualifiers'].str.replace("'","").str.strip("[").str.strip("]")
            
            record_df.rename(columns={'value':col_name,
                                      'dateTime':'datetime',
                                      'qualifiers':col_name + '_cd'}, inplace=True)
            record_df['site_no'] = site_no
            #return record_df
            #proper update procedure
            df = update_merge(df, record_df, on=['datetime','site_no'],
                              up=[col_name, col_cd_name])
            
    return df

# XXX This entire function should be merged into the get json
def get_latest(sites=None, state=None):
    """Gets latest record from select sites 
    """
    url = 'https://waterservices.usgs.gov/nwis/iv/'
    payload = {'siteStatus':'all', 'format':'json'}
    
    if state:
        payload['stateCd'] = state
    
    elif sites:
        payload['sites'] = to_str(sites)
        
    else:
        pass
    #XXX raise exception
    
    req = requests.get(url, params=payload)
    req.raise_for_status()

    return req.json()

def update_merge(left, right, on, up):
    """Performs a combination 
    Args:
    left,right - df
    on -list
    up -list
    """
    df = left.merge(right, how='outer', on=on) 
    
    # for columns in up
    for c in up:
        if c in left.columns:
            #print(c)
            df[c] = df[c+'_y'].fillna(df[c+'_x'])
            df[c] = df[c+'_y'].fillna(df[c+'_x'])
            df.drop([c + '_x', c+ '_y'], axis=1, inplace=True)
    
    return df