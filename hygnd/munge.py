from math import floor
import pandas as pd

def filter_param_cd(df, code):
    """Return df filtered by approved data
    """
    approved_df = df.copy()

    params = [param.strip('_cd') for param in df.columns if param.endswith('_cd')]


    for param in params:
        #filter out records where param_cd doesn't contain 'A' for approved.
        approved_df[param].where(approved_df[param + '_cd'].str.contains(code), inplace=True)

    # drop any rows where all params are nan and return
    return approved_df.dropna(axis=0, how='all', subset=params)


def interp_to_freq(df, freq=15, interp_limit=120, fields=None):
    """
    WARNING: for now this only works on one site at a time,
    Also must review this function further

    Args:
        df (DataFrame): a dataframe with a datetime index
        freq (int): frequency in minutes
        interp_limit (int): max time to interpolate over

    Returns:
        DataFrame

    """
    #XXX assumes no? multiindex
    df = df.copy()
    #df.reset_index(level=0, inplace=True)
    limit = floor(interp_limit/freq)
    freq_str = '{}min'.format(freq)
    start = df.index[0]
    end   = df.index[-1]
    new_index = pd.date_range(start=start, end=end, periods=None, freq=freq_str)
    new_index = new_index.union(df.index)

    new_df    = pd.DataFrame(index=new_index)
    new_df    = pd.concat([new_df, df], axis=1)

    out_df = new_df.interpolate(method='time',limit=limit).asfreq(freq_str)
    out_df.index.name = 'datetime'
    return out_df
    #out_df.set_index('site_no', append=True, inplace=True)
    #return out_df.reorder_levels(['site_no','datetime'])

def fill_iv_w_dv(iv_df, dv_df, freq='15min', col='00060'):
    """Fill gaps in an instantaneous discharge record with daily average estimates

    Args:
        iv_df (DataFrame): instantaneous discharge record
        dv_df (DataFrame): Average daily discharge record.
        freq (int): frequency of iv record

    Returns:
        DataFrame: filled-in discharge record

    """
    #double brackets makes this a dataframe
    updating_field = dv_df[[col]].asfreq(freq).ffill()

    updating_field = updating_field.rename(axis='columns',
                                           mapper={'00060_Mean':'00060'},
                                           inplace=True
                                          )

    iv_df.update(updating_field, overwrite=False)
    #return update_merge(iv_df, updating_field, na_only=True)
    return iv_df


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
