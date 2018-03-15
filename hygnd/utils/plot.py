import matplotlib.ticker as tkr
import matplotlib.pyplot as plt

#MARK_SIZE = 3 # not used

def nitrate_plot(df, df2, filename=None):
    """
    Args:
        df: df containing nitrate and discharge
        df2: df containing nitrate samples
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.subplots_adjust(hspace=0.15)
    
    #XXX maybe load computation is best outside this function
    load = df.Discharge * df.NitrateSurr * 0.00269688566 #XXX check this, 
    ax1.plot(df.index, df.Discharge, color='cornflowerblue', label='Discharge')
    ax2.plot(df.index,df.NitrateSurr, color='green', label='Nitrate probe observation')
    ax2.plot(df2.index,df2.Nitrate, marker='o', markerfacecolor='yellow', linewidth=0, label='Nitrate sample')
    ax3.plot(load.index, load.values, color='black', label='Load')
    
    
    #set labels
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Nitrate, in mg/L')
    ax3.set_ylabel('Nitrate, in tons/day')
    
    #format y-axis tick labels to include commas for thousands
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax2.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.1f'))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    
    #remove x tick labels on axes 1 and 2
    #ax1.get_xaxis().set_ticklabels([])
    #ax2.get_xaxis().set_ticklabels([])
    
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
    

#XXX: can this be generalized along with nitrate plot?
def ssc_plot(df, df2, filename=None):
    """See nitrate plot

    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.subplots_adjust(hspace=0.15)
    
    #XXX maybe load computation is best outside this function
    #load = df.Discharge * df.Turb_YSI * 0.00269688566 #XXX check this, 
    ax1.plot(df.index, df.Discharge, color='cornflowerblue', label='Discharge')
    
    
    #ax2.plot(df.index,df.Turb_YSI, color='green', label='Nitrate probe observation')
    #ax2.plot(df2.index,df2.SSC, marker='o', markerfacecolor='yellow', linewidth=0, label='Nitrate sample')
    #ax3.plot(load.index, load.values, color='black', label='Load')
    
    
    #set y-axis labels
    ax1.set_ylabel('Streamflow, in cfs')
    ax2.set_ylabel('Suspended sediment, in mg/L')
    ax3.set_ylabel('Suspended sediment, in tons/day')  
    
    #format y-axis tick labels to include commas for thousands
    ax1.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax2.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    ax3.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x),',')))
    
    if filename:
        
        plt.savefig(filename, bbox_inches='tight')
    
    
def ssc_model_plot():
    pass

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