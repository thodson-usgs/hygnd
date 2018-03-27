from math import floor
import pandas as pd

def interp_to_freq(df, freq=15, interp_limit=120):
    
    """
    Args:
        df (DataFrame): a dataframe with a datetime index
        freq (int): frequency in minutes
        interp_limit (int): max time to interpolate over
        
    Returns:
        DataFrame
        
    """
    limit = floor(interp_limit/freq)
    freq_str = '{}min'.format(freq)
    start = df.index[0]
    end   = df.index[-1]
    new_index = pd.date_range(start=start, end=end, periods=None, freq=freq_str)
    new_index = new_index.union(df.index)
    
    new_df    = pd.DataFrame(index=new_index)
    new_df    = pd.concat([new_df, df], axis=1)
    
    return new_df.interpolate(method='time',limit=limit).asfreq(freq_str)

#TODO: can we detect the freq in the iv record as opposed to defining it in a param
def update_Q_w_DQ(iv_df, dv_df, freq=15, Q_col='Discharge', DQ_col='DailyQ'):
    """Fill gaps in an instantaneous discharge record with daily average estimates
    
    Args:
        iv_df (DataFrame): instantaneous discharge record
        dv_df (DataFrame): Average daily discharge record.
        freq (int): frequency of iv record
    
    Returns:
        DataFrame: filled-in discharge record
        
    """
    freq_str = '{}min'.format(freq)
    
    dv_flow    = dv_df.rename(columns={'DailyQ':'Discharge'}) 
    dv_flow    = dv_flow.asfreq(freq).interpolate()
    
    return iv_flow.update(dv_flow, overwrite=False)

#This function may be deprecated once pandas.update support joins besides left.
def update_merge(left, right, na_only=False, on=None):
    """Performs a combination 
    Args:
    left (DataFrame): original data
    right (DataFrame): updated data
    na_only (bool): if True, only update na values
    """
    df = left.merge(right, how='outer',
                    left_index=True, right_index=True) 
    
    # check for column overlap and resolve update
    for column in df.columns:
        #if duplicated column, use the value from right
        if column[-2:] == '_x':
            name = column[:-2] # find column name
            
            if na_only:
                df[name] = df[name+'_x'].fillna(df[name+'_y'])
                
            else:
                df[name] = df[name+'_x'].update(df[name+'_y'])
        
            df.drop([name + '_x', name + '_y'], axis=1, inplace=True)
            
    return df