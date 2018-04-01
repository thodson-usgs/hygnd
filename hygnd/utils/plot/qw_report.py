import matplotlib.ticker as tkr
import matplotlib.pyplot as plt
from said.surrogatemodel import SurrogateRatingModel
from linearmodel.datamanager import DataManager
from hygnd.datasets.codes import pc
from hygnd.munge import update_merge
import os
#MARK_SIZE = 3 # not used

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
    
    nitrate_plot(con_data, sur_data, filename='plots/{}_nitrate.png'.format(site['name']), 
                 title=site['name'])
    ssc_model = ssc_plot(con_data, sur_data, filename='plots/{}_ssc.png'.format(site['name']),
            return_model=True, title=site['name'])
    
    for directory in ['model_data','report']:
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)    
    #output model data to tabel for colin
    df = ssc_model.get_model_dataset()
    df.to_csv('model_data/{}_ssc.csv'.format(site['name']))
    
    #write ssc model report
    reportfile = 'report/{}_ssc_report.txt'
    with open(reportfile, 'w') as f:
        f.write(ssc_model.get_model_report().as_text())
    
    plot_model(ssc_model, filename='plots/{}_ssc_model.png'.format(site['name']), title=site['name'])
    
    # try to plot phosphate
    try:
        phos_plot(con_data, sur_data, filename='plots/{}_p.png'.format(site['name']), title=site['name'])
    except:
        print('phospate didnt work')
    
    
def plot_model(model, filename=None, title=None):
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(15,4))
    
    model.plot(ax=ax1)
    
    model.plot(plot_type='quantile', ax=ax2)
    
    if title:     
        fig.suptitle(title)
    
    if filename:
        plt.savefig(filename)
        
#XXX: procedure for creating fixed interval record
def make_ssc_model(con_data, sur_data):
        
    rating_model = SurrogateRatingModel(con_data,
                                        sur_data,
                                        constituent_variable= 'SSC',
                                        surrogate_variables= ['Turb_YSI'], 
                                        match_method='mean', match_time=30)
    
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
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
    
import matplotlib.ticker as tkr
import matplotlib.pyplot as plt
from said.surrogatemodel import SurrogateRatingModel
from linearmodel.datamanager import DataManager
from hygnd.datasets.codes import pc
#MARK_SIZE = 3 # not used

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
        
#XXX: procedure for creating fixed interval record
def make_ssc_model(con_data, sur_data):
        
    rating_model = SurrogateRatingModel(con_data,
                                        sur_data,
                                        constituent_variable= 'SSC',
                                        surrogate_variables= ['Turb_YSI'], 
                                        match_method='mean', match_time=30)
    
    rating_model.set_surrogate_transform(['log10'], surrogate_variable='Turb_YSI')
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
                                                            bias_correction=False,
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
    
    #XXX maybe load computation is best outside this function
    load = df.Discharge * df.NitrateSurr * 0.00269688566 #XXX check this, 
    ax1.plot(df.index, df.Discharge, color='cornflowerblue', label='Discharge')
    ax2.plot(df.index,df.NitrateSurr, color='green', label='Nitrate probe observation')
    ax2.plot(df2.index,df2.Nitrate, marker='o', markerfacecolor='yellow', linewidth=0, label='Nitrate sample')
    #TODO update this plotting, add 0.5mg min error
    u90 = 
    ax2.fill_between(df.index, df.NitrateSurr*.9, df.NitrateSurr*1.1, facecolor='gray',
                    edgecolor='gray', alpha=0.5, #interpolate=True,
                    label='90% Prediction Interval')
    
    ax3.plot(load.index, load.values, color='black', label='Load')
    
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
    
def phos_plot(con_data, sur_data, filename=None, title=None):
    """
    """
    #TODO: separate into model function
    #develop rating model on ortho-P and turbidity
    rating_model_1 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['OrthoP','Turb_YSI'],
                                          match_method='mean',
                                          match_time=120)
    
    rating_model_2 = SurrogateRatingModel(con_data,
                                          sur_data, 
                                          constituent_variable='TP',
                                          surrogate_variables=['Turb_YSI'],
                                          match_method='mean',
                                          match_time=30)
    
    df = sur_data.get_data()
    df2 = rating_model_1.get_model_dataset()
    df3 = rating_model_2.get_model_dataset()

    predicted_data_2   = rating_model_2._model.predict_response_variable(explanatory_data=rating_model_2._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=False,
                                                            prediction_interval=True)
 
    predicted_data_1 = rating_model_1._model.predict_response_variable(explanatory_data=rating_model_1._surrogate_data,
                                                            raw_response=True,
                                                            bias_correction=False,
                                                            prediction_interval=True)
    #fill gaps in OP-Turb model with Turb only model`
    predicted_data_1 = update_merge(predicted_data_1,
                                    predicted_data_2, na_only=True)
    
    
    
    #leave in plotting function
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(15,10))
    fig.subplots_adjust(hspace=0.15)
    
     
    ax1.plot(df.index, df['Discharge'])
    #TODO include all obs from other models 
    obs = rating_model_1.get_model_dataset()
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