from usgs_tools.core import *

import pandas as pd
import requests
import json

def sample_gage_record():
    
    return get_gage_json('05586300','2016-10-1','2017-9-30','nitrate','temperature')
###############################################################################



def get_gage_json(site, start, end, *args):
    """Function to get gage data

    Args:
        site (string): X digit USGS site ID. 05586300
        start: 2018-01-25
        end:
        args: list of data fields

    Returns:
        Return an object containing the gage record
        
    
    See https://waterdata.usgs.gov/nwis?automated_retrieval_info

    """ 
    url = 'https://waterservices.usgs.gov/nwis/iv/'
    payload = {'sites':site, 'startDT':start, 'endDT':end, 
               'format':'json'} #, 'parameterCD':''} 
    parameters = []
   
    req = requests.get(url, params=payload)
    req.raise_for_status()

    return req.json()


def parse_gage_json(json):
    """Parses an NWIS json into a pandas DataFrame
    
    Args:
        json (dict)
    
    """
    
    df = pd.DataFrame( columns=['datetime','site_no'] )
    
    import ipdb; ipdb.set_trace()
    for timeseries in json['value']['timeSeries']:
        #get site_no associated with timeseries
        site_no = timeseries['sourceInfo']['siteCode'][0]['value']
        param_cd = timeseries['variable']['variableCode'][0]['value']
       
        # loop through each parameter in timeseries. This is mainly relevant to turbidity
        for parameter in timeseries['values']:
            col_name = param_cd 
            
            if len(timeseries['values']) > 1:
                   col_name = col_name + parameter['method'][0]['methodDescription']
            
            record_json = parameter['value']  
            record_json = str(record_json).replace("'",'"')
            record_df   = pd.read_json(record_json, orient='records')
            
            record_df.rename(columns={'value':col_name,
                                      'dateTime':'datetime',
                                      'qualifiers':col_name + '_cd'}, inplace=True)
            
            record_df['site_no'] = site_no
            
                
            df = df.merge(record_df, how='outer')#, on=['datetime','site_no'])#,'site_no'])
    
    return df