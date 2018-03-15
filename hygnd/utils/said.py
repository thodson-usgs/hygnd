import os

# move some of these dicts over into said.py
from usgs_tools.datasets.codes import said_sites, nwis_to_said, said_files 

from usgs_tools.portals.nwis import *# import get_records and to_str

from linearmodel.datamanager import DataManager

SAID_DATE_FMT = '%m/%d/%Y %H:%M'


#Generate SAID input samples from NWIS
def create_SAID_sample_txt(river_cd, path):
    
    params = ['p00665','p80154','p00631','p70331']
    out_cols = ['datetime'] + params
    river_name = said_sites[river_cd][0]
    start = said_sites[river_cd][1]
    df = get_samples(river_cd, start=start)
    filename = "{}{}{}_Constituent.txt".format(path, os.sep, river_name)
    df = df[out_cols]
    df.dropna(axis=0, how='all', subset=params, inplace=True)
    header = [nwis_to_said[i] for i in out_cols]
    
    df.to_csv(path_or_buf=filename, sep='\t', index=False,
              header=header,
              date_format = SAID_DATE_FMT)
   

#Generate SAID input records from NWIS. Filter only approved records
def create_SAID_txt(river_cd, param_group, path):
    """
    
    Args:
        param_group: 'Surrogate' or 'OrthoP or DailyQ'
    """
    #get json
    
    #parse json
    river_name = said_sites[river_cd][0]
    start      = said_sites[river_cd][1]
    param_dict = said_files[param_group]
    
    param_cd = list(param_dict.keys())
    
    # get records from nwis
    if param_group == 'DailyQ':
        json = get_gage_json(river_cd, start=start, params=param_cd, freq='dv')
        #XXX evently we won't use daily values 
    else:
        json = get_gage_json(river_cd, start=start, params=param_cd)
    
    df = parse_gage_json(json)
    #delete any unapproved records
    df_params = df.columns.drop('datetime').drop('site_no')
    df_params = [p for p in df_params if '_cd' not in p]
    
    for param in df_params:
        df[param].where(df[param + '_cd'] == 'A', inplace=True)
    
    #now format output database
    out_cols = ['datetime'] + df_params
    out_df = df[out_cols]

    
    #drop any rows where all fields are empty
    out_df = out_df.dropna(axis=0, how='all', subset=df_params)
    #sort by date
    out_df.sort_values(by=['datetime'], inplace=True)
    
    #format header for output txt
    header = [nwis_to_said[i] for i in out_df.columns]
    #create output filename
    filename = "{}{}{}_{}.txt".format(path, os.sep, river_name, param_group)
    
    #export to tsv with filename and new headers
    out_df.to_csv(path_or_buf=filename, sep='\t', index=False,
                  columns=out_cols,
                  header=header,
                  date_format = SAID_DATE_FMT)
   

def setup_SAID(path):
    """ Generate all SAID files for all sites
    """
    param_groups = said_files.keys()
    sites = list(said_sites.keys()) ##remove this list after testing
    #XXX sites = [sites[0]]
    
    for site in sites:
        
        create_SAID_sample_txt(site, path)
        
        for param_group in param_groups:
            print(param_group)
            create_SAID_txt(site, param_group, path)

# consider making this a method of the DataManger class
def update_Q_w_DQ(iv_flow_dm, dv_flow_dm, freq='60min'):
    '''return datamanager opbject in which gaps in discharge have been in-filled with the daily average discharge
    '''
    iv_flow = flow_dm.get_data() #dataframe with instant. flow data
    iv_flow = original_flow.asfreq(freq).ffill(limit = 1) 
    
    dv_flow    = dv_flow_dm.get_data().rename(columns={'DailyQ':'Discharge'}) 
    dv_flow    = dv_flow.asfreq(freq).interpolate()
    
    iv_flow.update(dv_flow, overwrite=False)
    
    updated_flow = DataManager(iv_flow, iv_flow_dm.get_origin()) #XXX add dv_flow origin
    
    return updated_flow
    
def plot_load(discharge_df, iv_df, smpl_df):
    
    fig = plt.figure()
    ax1 = fig.add_subplot(311) 
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    
    #plot discharge
    ax1.plot(discharge_df.index, )
    
def run_SAID_ipynb(path):
    """
    """
    pass