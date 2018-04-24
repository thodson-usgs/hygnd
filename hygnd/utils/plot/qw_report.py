import matplotlib.ticker as tkr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
from said.surrogatemodel import SurrogateRatingModel
from linearmodel.datamanager import DataManager
from hygnd.datasets.codes import pc
from hygnd.munge import update_merge
import os
import numpy as np
import pandas as pd
#MARK_SIZE = 3 # not used
SUMMARY_COLS = ['model','# obs','adjusted r^2','p-value']
HP_FIGSIZE = (7.5,5) #Half page figsize
DPI = 150
MODEL_FIGSIZE = (7.5,9)

mpl.rcParams.update({'font.size':8})
mpl.rcParams['lines.linewidth'] = 1

#FLUX_CONV = 0.00269688566

# Conversions
mg2lbs = 2.20462e-6
l2cf = 1/0.0353137
min2sec = 60
lbs2ton = 0.0005
interval = 15 * min2sec

FLUX_CONV = mg2lbs * l2cf * interval


def phos_load(wy, model1, model2):
    start = str(wy-1) + '-10-01'
    end   = str(wy) + '-09-30'
    
    predicted_data_1   = model1._model.predict_response_variable(explanatory_data=model1._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
    
    obs = model1.get_model_dataset()
    
    df = model1._surrogate_data.get_data()
    
    if model2:
        
        pvalue = model2._model._model.fit().f_pvalue
        
        if pvalue < 0.05:
            obs = obs[~obs['Missing']]
            obs2 = model2.get_model_dataset()
            obs2.drop(obs.index, axis=0) #drop anything thats in obs1 from obs2
            obs = obs.append(obs2).sort_index()
    
        
            predicted_data_2 = model2._model.predict_response_variable(explanatory_data=model2._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)    
 
            predicted_data_1 = update_merge(predicted_data_2, predicted_data_1, na_only=True)
    flux = df['Discharge'] * predicted_data_1['TP'] * FLUX_CONV
    
    return flux.loc[start:end].sum()
    
def nitrate_load(wy, sur_data):
    df = sur_data.get_data()
    start = str(wy-1) + '-10-01'
    end   = str(wy) + '-09-30'

    
    flux  = df['NitrateSurr'] * df['Discharge']  * FLUX_CONV #XXX check this, 
    #return flux
    return flux.loc[start:end].sum()

def ssc_load(wy, con_data, sur_data):
    """calc ssc load for water year
    """
    df = sur_data.get_data()
    start = str(wy-1) + '-10-01'
    end   = str(wy) + '-09-30'
    
    rating_model = make_ssc_model(con_data, sur_data)

    predicted_data = rating_model._model.predict_response_variable(explanatory_data=rating_model._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
    
    flux = df.Discharge * predicted_data['SSC'] * FLUX_CONV #XXX check this, 
    return flux.loc[start:end].sum()


def load_report(wy,store, site):
    filename = 'reports/loads_{}.txt'.format(str(wy))
    
    try:
        sur_df = store.get('/site/{}/said/iv'.format(site['id']))
        con_df = store.get('/site/{}/said/qwdata'.format(site['id']))
    
    except KeyError:
        print('site {} not found'.format(site['name']))

    sur_data = DataManager(sur_df)
    con_data = DataManager(con_df)
    
    N = nitrate_load(wy, sur_data)
    SSC = ssc_load(wy, con_data, sur_data)
    
    p_model1, p_model2 = make_phos_model(con_data, sur_data)
    TP = phos_load(wy, p_model1, p_model2)
    
    with open(filename,'a') as f:
        f.write('site: {}, Nitrate: {}, TP: {}, SSC: {}\n'.format(site['id'],
                                                                  N,
                                                                  TP,
                                                                  SSC * lbs2ton))
    
def gen_report(store, site):
    """Generates a plots and model data for a given site
    """
    try:
        sur_df = store.get('/site/{}/said/iv'.format(site['id']))
        con_df = store.get('/site/{}/said/qwdata'.format(site['id']))
    
    except KeyError:
        print('site {} not found'.format(site['name']))

    sur_data = DataManager(sur_df)
    con_data = DataManager(con_df)
    
    summary_table = pd.DataFrame(columns=SUMMARY_COLS)
    
    nitrate_plot(con_data, sur_data, filename='plots/{}_nitrate.png'.format(site['name']))
    
    ssc_model = ssc_plot(con_data, sur_data, filename='plots/{}_ssc.png'.format(site['name']),
            return_model=True)
    #append the model results to summary
    summary_table= summary_table.append(model_row_summary(ssc_model))
    
    for directory in ['model_data','report']:
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)
            
    #output model input data
    df = ssc_model.get_model_dataset()
    df.to_csv('model_data/{}_ssc.csv'.format(site['name']))
    
    #output prediction
    
    #write ssc model report
    reportfile = 'report/{}_ssc_report.txt'.format(site['name'])
    with open(reportfile, 'w') as f:
        f.write(ssc_model.get_model_report().as_text())
    
    p_model1, p_model2 = make_phos_model(con_data, sur_data)
    
    #df_p1 = p_model1.get_model_dataset()
    predicted_p = p_model1._model.predict_response_variable(explanatory_data=p_model1._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
    
    predicted_p.to_csv('model_data/{}_tp.csv'.format(site['name']))
    
    summary_table= summary_table.append(model_row_summary(p_model1))
    summary_table= summary_table.append(model_row_summary(p_model2))
    
    
    plot_model2(ssc_model, filename='plots/{}_ssc_model.png'.format(site['name']))
    
    phos_plot2(p_model1, p_model2, filename='plots/{}_tp.png'.format(site['name']))
    
    plot_model2(p_model1, filename='plots/{}_orthoP_model.png'.format(site['name']))
    #
    ## try to plot phosphate
    #try:
    #    phos_plot(con_data, sur_data, filename='plots/{}_p.png'.format(site['name']), title=site['name'],
    #             return_model=True)
    #except:
    #    print('phospate plot didnt work')
    #
    summary_table.to_csv('report/{}_model_summary.csv'.format(site['name']),
                        index=False)
    
    
    #write loads to file

    

def make_phos_model(con_data, sur_data):
    
    rating_model_1 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['Turb_YSI'],#,'Discharge'],
                                          match_method='nearest',
                                          match_time=30)
    
    rating_model_1.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
    rating_model_1.set_constituent_transform('log10')
    
    try:
        rating_model_2 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['OrthoP','Turb_YSI'],
                                          match_method='nearest',
                                          match_time=30)
        
        rating_model_2.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
        rating_model_2.set_surrogate_transform(['log10'], surrogate_variable='OrthoP')
        rating_model_2.set_constituent_transform('log10')
    
        
        pvalue = rating_model_2._model._model.fit().f_pvalue
        #reject insignificant models
        #import pdb; pdb.set_trace()
        # move rejection elsewhere
        #if pvalue > 0.05 or pvalue < 0 or np.isnan(pvalue):
        #    rating_model_2 = None
    except:#
        rating_model_2 = None
    
    return rating_model_1, rating_model_2


def plot_model2(model, filename=None, title=None):
    
    plt.figure(figsize=MODEL_FIGSIZE)
    G = gridspec.GridSpec(3,2)
    ax1 = plt.subplot(G[0,0])
    ax2 = plt.subplot(G[0,1])
    ax3 = plt.subplot(G[1,0])
    ax4 = plt.subplot(G[1,1])
    ax5 = plt.subplot(G[-1, :])
    #fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(15,8))
    
    model.plot(plot_type='model_pred_vs_obs', ax=ax1)
    model.plot(plot_type='resid_probability', ax=ax2)
    model.plot(plot_type='resid_vs_fitted', ax=ax3)
    model.plot(plot_type='quantile', ax=ax4)
    model.plot(plot_type='resid_vs_time', ax=ax5)
    
    #plt.tight_layout()
    
    if title:     
        plt.suptitle(title)
    
    if filename:
        plt.savefig(filename, bbox_inches = 'tight')
        
#XXX: procedure for creating fixed interval record
def make_ssc_model(con_data, sur_data):
        
    rating_model = SurrogateRatingModel(con_data,
                                        sur_data,
                                        constituent_variable= 'SSC',
                                        surrogate_variables= ['Turb_YSI'], 
                                        match_method='nearest', match_time=30)
    
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
    rating_model.set_constituent_transform('log10')
    # remove fliers
    df = rating_model.get_model_dataset()
    fliers = df[(df['Raw Residual'] > 0.9) | (df['Raw Residual'] < -0.9)].index
    rating_model.exclude_observations(fliers)
    
    return rating_model

def ssc_plot(con_data, sur_data, filename=None, return_model=False, title=None):
    """ Generate plots of discharge, predicted SSC, and sediment load.
    
    Args:
        con_data: constituent DataManager
        sur_data: surrogate DataManager
    """
    
    rating_model = make_ssc_model(con_data, sur_data)
    
    df = sur_data.get_data()
    obs = rating_model.get_model_dataset()

    predicted_data = rating_model._model.predict_response_variable(explanatory_data=rating_model._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
    
    #predicted_data['SSC_l90'] = np.maximum(0,predicted_data['SSC_l90'])
    #resample to hour filling in at most 2 hours of missing data
    #predicted_data = predicted_data.dropna().resample('60min').ffill(limit=2)
                                                       
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=HP_FIGSIZE, dpi=DPI)
    fig.subplots_adjust(hspace=0)
    
    ax1.plot(df.index, df['Discharge'])
    
    plot_prediction_ts(predicted_data, obs, 'SSC', ax2, color='olive')
    #rating_model.plot('time series', ax2)
   
    load = df.Discharge * predicted_data['SSC'] * 0.00269688566 #XXX check this, 
    
    #ax2.set_ylim(bottom=0)
    plot_load_ts(predicted_data, df.Discharge, 'SSC', ax3)
    #ax3.plot(load.index, load.values, color='black', label='load')
   
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Suspended sediment, in mg/L')
    ax3.set_ylabel('Suspended sediment, in tons/day')
    
    #set grid
    for ax in (ax1, ax2, ax3):
        ax.grid(which='major',axis='x',linestyle='--')
        #/ax.xaxis.grid() # vertical lines
    
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax2.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    fig.autofmt_xdate()
    
    if title:
        fig.suptitle(title)
    
    if filename:
        
        fig.savefig(filename, bbox_inches='tight')
        
    else: 
        fig.show()
    
    #return predicted_data
    if return_model:
        return rating_model


    
def nitrate_plot(con_data, sur_data, filename=None, title=None):
    """
    Args:
        df: df containing nitrate and discharge
        df2: df containing nitrate samples
    """
    df2 = con_data.get_data()
    df = sur_data.get_data()
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=HP_FIGSIZE, dpi=DPI)
    fig.subplots_adjust(hspace=0)
    
    ax1.plot(df.index, df.Discharge, color='cornflowerblue', label='Discharge')
    ax2.plot(df.index,df.NitrateSurr, color='green', label='Nitrate probe observation')
    ax2.plot(df2.index,df2.Nitrate, marker='o', markerfacecolor='yellow', linewidth=0, label='Nitrate sample', ms=4)
    
    #error is the greater of 0.5mg/L or 10% of the measurement 
    n_error = np.maximum(0.5, df['NitrateSurr']*.1)
    df['NitrateSurr_u90'] = df.NitrateSurr + n_error
    df['NitrateSurr_l90'] = df.NitrateSurr - n_error
    #clip values below 0
    df['NitrateSurr_l90'] = np.maximum(0, df['NitrateSurr_l90'])
    
    ax2.fill_between(df.index, df.NitrateSurr_l90, df.NitrateSurr_u90, facecolor='gray',
                    edgecolor='gray', alpha=0.5, #interpolate=True,
                    label='90% Prediction Interval')
    
    load = df.Discharge * df.NitrateSurr * 0.00269688566 #XXX check this,
    load_u90 = df.Discharge * df.NitrateSurr_u90 * 0.00269688566 #XXX check this,
    load_l90 = df.Discharge * df.NitrateSurr_l90 * 0.00269688566 #XXX check this,
    
    ax3.plot(load.index, load.values, color='black', label='Load')
    ax3.fill_between(load.index, load_l90, load_u90, facecolor='gray',
                    edgecolor='gray', alpha=0.5, #interpolate=True,
                    label='90% Prediction Interval')
    
    
    if title:
        fig.suptitle(title)
    #set labels
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Nitrate, in mg/L')
    ax3.set_ylabel('Nitrate, in tons/day')
    
    #set grid
    for ax in (ax1, ax2, ax3):
        ax.grid(which='major',axis='x',linestyle='--')
    
    #format y-axis tick labels to include commas for thousands
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax2.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.1f'))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    
    
    #align yaxis labels
    #ax1.get_yaxis().set_label_coords(-.05, .5)
    #ax2.get_yaxis().set_label_coords(-.05, .5)
    #ax3.get_yaxis().set_label_coords(-.05, .5)
    
    #create legend(s), set figure size, save figure
    ax2.legend(loc='best', numpoints=1)
    #fig.set_size_inches(15,10)
    fig.autofmt_xdate()
    
    if filename:
        
        plt.savefig(filename, bbox_inches = 'tight')

def model_row_summary(model):
    if not model:
        return None
    
    res = model._model._model.fit()
    columns = SUMMARY_COLS
    row = [[
        model._model.get_model_formula(),
        res.nobs,
        res.rsquared_adj,
        res.f_pvalue     
    ]]
    
    return pd.DataFrame(row, columns=columns)
           

def predictions_to_txt(model, site):
    predicted_data = model._model.predict_response_variable(explanatory_data=model._surrogate_data,
                                                           raw_response=True,
                                                           bias_correction=True,
                                                           prediction_interval=True)
    constituent = model2.get_constituent_variable()
    predicted_data.to_csv('model_data/{}_{}.csv',format('site',constituent))
    
def phos_plot2(model1, model2, filename=None, title=None):
    
    #df = sur_data.get_data()
    #df3 = rating_model_2.get_model_dataset()

    #XXX bias correction true?
    predicted_data_1   = model1._model.predict_response_variable(explanatory_data=model1._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
   
    obs = model1.get_model_dataset()
    
    df = model1._surrogate_data.get_data()
    
    if model2:
        
        pvalue = model2._model._model.fit().f_pvalue
        
        if pvalue < 0.05:
            obs = obs[~obs['Missing']]
            obs2 = model2.get_model_dataset()
            obs2.drop(obs.index, axis=0) #drop anything thats in obs1 from obs2
            obs = obs.append(obs2).sort_index()
    
        
            predicted_data_2 = model2._model.predict_response_variable(explanatory_data=model2._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)    
            #fill gaps in OP-Turb model with Turb only model`
            #return predicted_data_1, predicted_data_2
            predicted_data_1 = update_merge(predicted_data_2,
                                            predicted_data_1, na_only=True)
            
    # make plot
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=HP_FIGSIZE, dpi=DPI)
    fig.subplots_adjust(hspace=0)
    
     
    ax1.plot(df.index, df['Discharge']) 
    
    plot_prediction_ts(predicted_data_1, obs, 'TP', ax2, color='maroon')

    plot_load_ts(predicted_data_1, df.Discharge, 'TP', ax3)
    #load = df.Discharge * predicted_data_1['TP'] * 0.00269688566 #XXX check this, 
    
    ax2.set_ylim(bottom=0)
    
    #ax3.plot(load.index, load.values, color='black', label='load')
    
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('TP, in mg/L')
    ax3.set_ylabel('TP, in tons/day')
    
    #set grid
    for ax in (ax1, ax2, ax3):
        ax.grid(which='major',axis='x',linestyle='--')
    
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    
    fig.autofmt_xdate()
   
    if title:
        fig.suptitle(title)
    if filename:
        
        plt.savefig(filename, bbox_inches='tight')
    
   

    
    
#generalise this function for any
def plot_log(record,samples, filename=None):
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    ax1.plot(record.index, record.values, color='gray')
   
    
    ax2.plot(samples.index, samples.values, marker='o',
             markerfacecolor='yellow', markeredgecolor='black',
            linewidth=0)
    
    fig.autofmt_xdate()
    
    if filename:
        
        plt.savefig(filename, bbox_inches = 'tight')
        
def site_report(site_no, ):
    pass
    #munge data
    
    #plot nitrate
    
    #plot ssc
    
    #generate model report
    
    #plot phosphate
    
def plot_prediction_ts(data, obs, response_var, ax, color='blue'):
    L90 = '{}_L90.0'.format(response_var)
    U90 = '{}_U90.0'.format(response_var)
    #obs = rating_model.get_model_dataset()
    
    ax.plot(data.index, data[response_var], color=color, 
            label='Predicted {}'.format(response_var))
    
    ax.fill_between(data.index, data[L90], data[U90], facecolor='gray',
                    edgecolor='gray', alpha=0.5, #interpolate=True,
                    label='90% Prediction Interval')
    
    #get observations
    included = obs[~obs['Missing'] & ~obs['Excluded']][response_var]
    missing  = obs[obs['Missing']][response_var]
    excluded  = obs[obs['Excluded']][response_var]
    #con_obs = model_dataset[response_var]
    
    ax.plot(missing.index, missing.values, marker='o', label='Missing',
            markeredgecolor='black', markerfacecolor='None', linestyle='None',ms=4)
    ax.plot(included.index, included.values, marker='o', label='Included',
            markerfacecolor='yellow', markeredgecolor='black',linestyle='None',ms=4)
    ax.plot(excluded.index, excluded.values, marker='x', label='Excluded',
            markerfacecolor='red', markeredgecolor='red',linestyle='None',ms=4)
    
    ax.legend(loc='best') 
    #ax.set_ylabel('TP')

def plot_load_ts(data, discharge, response_var, ax, color='black'):
    
    LOAD_CONV = 0.00269688566 #XXX check
    L90 = '{}_L90.0'.format(response_var)
    U90 = '{}_U90.0'.format(response_var)
    
    load = discharge * data[response_var] * LOAD_CONV
    ax.plot(data.index, load, color=color)
    #load_l90 = discharge * data[L90] * LOAD_CONV
    #load_u90 = discharge * data[U90] * LOAD_CONV
    #ax.fill_between(data.index, load_l90, load_u90, facecolor='gray',
    #                edgecolor='gray', alpha=0.5, #interpolate=True,
    #                label='90% Prediction Interval')
    
    
