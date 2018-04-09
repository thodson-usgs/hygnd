import matplotlib.ticker as tkr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from said.surrogatemodel import SurrogateRatingModel
from linearmodel.datamanager import DataManager
from hygnd.datasets.codes import pc
from hygnd.munge import update_merge
import os
import numpy as np
import pandas as pd
#MARK_SIZE = 3 # not used
SUMMARY_COLS = ['model','# obs','adjusted r^2','p-value']

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
    
    nitrate_plot(con_data, sur_data, filename='plots/{}_nitrate.png'.format(site['name']), 
                 title=site['name'])
    
    ssc_model = ssc_plot(con_data, sur_data, filename='plots/{}_ssc.png'.format(site['name']),
            return_model=True, title=site['name'])
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
    
    
    plot_model2(ssc_model, filename='plots/{}_ssc_model.png'.format(site['name']), title=site['name'])
    
    phos_plot2(p_model1, p_model2, filename='plots/{}_tp.png'.format(site['name']), title=site['name'])
    
    plot_model2(p_model1, filename='plots/{}_orthoP_model.png'.format(site['name']), title=site['name'])
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
    

def make_phos_model(con_data, sur_data):
    
    rating_model_1 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['Turb_YSI','Discharge'],
                                          match_method='nearest',
                                          match_time=30)
    
    try:
        rating_model_2 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['OrthoP','Turb_YSI'],
                                          match_method='nearest',
                                          match_time=30)
        
        
        pvalue = rating_model_2._model._model.fit().f_pvalue
        #reject insignificant models
        #import pdb; pdb.set_trace()
        if pvalue > 0.05 or pvalue < 0 or np.isnan(pvalue):
            rating_model_2 = None
    except:#
        rating_model_2 = None
    
    return rating_model_1, rating_model_2
    
    
    
#XXX: procedure for creating fixed interval record
def make_ssc_model(con_data, sur_data):
        
    rating_model = SurrogateRatingModel(con_data,
                                        sur_data,
                                        constituent_variable= 'SSC',
                                        surrogate_variables= ['Turb_YSI','Discharge'], 
                                        match_method='mean', match_time=30)
    
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Discharge')
    rating_model.set_constituent_transform('log10')
    return rating_model

def ssc_plot(con_data, sur_data, filename=None, return_model=False, title=None):
    """ Generate plots of discharge, predicted SSC, and sediment load.
    
    Args:
        con_data: constituent /DataManager
        sur_data: surrogate DataManager
    """
    
    rating_model = make_ssc_model(con_data, sur_data)
    
    df = sur_data.get_data()
    obs = rating_model.get_model_dataset()

    predicted_data = rating_model._model.predict_response_variable(explanatory_data=rating_model._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=False,
                                                            prediction_interval=True)
    
    #resample to hour filling in at most 2 hours of missing data
    #predicted_data = predicted_data.dropna().resample('60min').ffill(limit=2)
                                                       
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(15,10))
    fig.subplots_adjust(hspace=0.15)
    

def plot_model(model, filename=None, title=None):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(15,8))
    
    model.plot(ax=ax1)
    model.plot(plot_type='variable_scatter', ax=ax2)
    model.plot(plot_type='model_pred_vs_obs', ax=ax3)
    model.plot(plot_type='quantile', ax=ax4)
    
    if title:     
        fig.suptitle(title)
    
    if filename:
        plt.savefig(filename)
        
def plot_model2(model, filename=None, title=None):
    
    plt.figure(figsize=(15, 10))
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
        plt.savefig(filename)
        
#XXX: procedure for creating fixed interval record
def make_ssc_model(con_data, sur_data):
        
    rating_model = SurrogateRatingModel(con_data,
                                        sur_data,
                                        constituent_variable= 'SSC',
                                        surrogate_variables= ['Turb_YSI','Discharge'], 
                                        match_method='nearest', match_time=30)
    
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Discharge')
    rating_model.set_constituent_transform('log10')
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
    
    #resample to hour filling in at most 2 hours of missing data
    #predicted_data = predicted_data.dropna().resample('60min').ffill(limit=2)
                                                       
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(15,10))
    fig.subplots_adjust(hspace=0.15)
    
    ax1.plot(df.index, df['Discharge'])
    
    plot_prediction_ts(predicted_data, obs, 'SSC', ax2, color='olive')
    #rating_model.plot('time series', ax2)
   
    load = df.Discharge * predicted_data['SSC'] * 0.00269688566 #XXX check this, 
    
    ax2.set_ylim(bottom=0)
    
    ax3.plot(load.index, load.values, color='black', label='load')
    
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Suspended sediment, in mg/L')
    ax3.set_ylabel('Suspended sediment, in tons/day')
    
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax2.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    
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
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.subplots_adjust(hspace=0.15)
    
    ax1.plot(df.index, df.Discharge, color='cornflowerblue', label='Discharge')
    ax2.plot(df.index,df.NitrateSurr, color='green', label='Nitrate probe observation')
    ax2.plot(df2.index,df2.Nitrate, marker='o', markerfacecolor='yellow', linewidth=0, label='Nitrate sample')
    
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
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Nitrate, in mg/L')
    ax3.set_ylabel('Nitrate, in tons/day')
    
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
    fig.set_size_inches(15,10)
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
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(15,10))
    fig.subplots_adjust(hspace=0.15)
    
     
    ax1.plot(df.index, df['Discharge'])
    
    
    plot_prediction_ts(predicted_data_1, obs, 'TP', ax2, color='maroon')
   
    load = df.Discharge * predicted_data_1['TP'] * 0.00269688566 #XXX check this, 
    
    ax2.set_ylim(bottom=0)
    
    ax3.plot(load.index, load.values, color='black', label='load')
    
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Total Phosphorus, in mg/L')
    ax3.set_ylabel('Total Phosphorus, in tons/day')
    
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
   
    if title:
        fig.suptitle(title)
    if filename:
        
        plt.savefig(filename, bbox_inches='tight')
    
   

    
def phos_plot(con_data, sur_data, filename=None, title=None):
    """
    """
    #TODO: separate into model function
    #develop rating model on ortho-P and turbidity
    #make turb model first, incase ortho model fails
    rating_model_1 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['Turb_YSI','Discharge'],
                                          match_method='nearest',
                                          match_time=30)
    
    
    
    df = sur_data.get_data()
    #df3 = rating_model_2.get_model_dataset()

    #XXX bias correction true?
    predicted_data_1   = rating_model_1._model.predict_response_variable(explanatory_data=rating_model_1._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)
 
    
   
    try:
        print('trying')
        rating_model_2 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['OrthoP','Turb_YSI'],
                                          match_method='nearest',
                                          match_time=120)
        pvalue = rating_model_2._model._model.fit().f_pvalue
        print(pvalue)
        #assert pvalue <= 0.05
        if pvalue <= 0.05:
        #df2 = rating_model_1.get_model_dataset()
            predicted_data_2 = rating_model_2._model.predict_response_variable(explanatory_data=rating_model_2._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=True,
                                                            prediction_interval=True)    
            #fill gaps in OP-Turb model with Turb only model`
            #return predicted_data_1, predicted_data_2
            predicted_data_1 = update_merge(predicted_data_2,
                                         predicted_data_1, na_only=True)
    
    except:
        print('couldnt make orthoP turb model')
        
    
    
    
    #leave in plotting function
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(15,10))
    fig.subplots_adjust(hspace=0.15)
    
     
    ax1.plot(df.index, df['Discharge'])
    
    # find all non-missing and compile within a single df
    #TODO color code obs by model
    obs1 = rating_model_1.get_model_dataset()
    obs2 = rating_model_2.get_model_dataset()
    
    obs1 = obs1[~obs1['Missing']]
    obs2.drop(obs1.index, axis=0) #drop anything thats in obs1 from obs2
    obs = obs1.append(obs2).sort_index()
    
    
    
    plot_prediction_ts(predicted_data_1, obs, 'TP', ax2, color='maroon')
   
    load = df.Discharge * predicted_data_1['TP'] * 0.00269688566 #XXX check this, 
    
    ax2.set_ylim(bottom=0)
    
    ax3.plot(load.index, load.values, color='black', label='load')
    
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Total Phosphorus, in mg/L')
    ax3.set_ylabel('Total Phosphorus, in tons/day')
    
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
   
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
    #con_obs = model_dataset[response_var]
    
    ax.plot(missing.index, missing.values, marker='o', label='Missing',
            markeredgecolor='black', markerfacecolor='None', linestyle='None')
    ax.plot(included.index, included.values, marker='o', label='Included',
            markerfacecolor='yellow', markeredgecolor='black',linestyle='None')
    
    ax.legend(loc='best') 
    #ax.set_ylabel('TP')