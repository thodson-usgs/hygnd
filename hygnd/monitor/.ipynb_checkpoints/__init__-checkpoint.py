
def status_table(df):
    """given a status df returned from NWIS create a table of parameters and times
    """
    cols = df.columns
    
    
    cols = [col for col in cols if '_cd' not in col]
    cols.remove('datetime')
    
    sites = df['site_no'].unique()
    
    status_df = pd.DataFrame(columns=cols)
    
    
    return status_df