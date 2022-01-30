# Keep functions here for visualizing data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_plotlines(rh_site, plotlines_dict, percentiles, percentile_keys):
    for index, percentile in enumerate(percentile_keys):
        plotlines_dict[percentile] = []
    # within each run, pull out flow percentiles from each row
    for row_index, _ in enumerate(rh_site['data'].iloc[:,0]): # loop through each row, 366 total
        # loop through all percentiles
        for index, percentile in enumerate(percentiles): 
            # calc flow percentiles across all years for each row of flow matrix
            flow_row = pd.to_numeric(rh_site['data'].iloc[row_index, :], errors='coerce')
            plotlines_dict[percentile_keys[index]].append(np.nanpercentile(flow_row, percentile))
    return plotlines_dict

def plot_rh(rgb_rh):
    percentiles = [10, 25, 50, 75, 90]
    percentile_keys = ['ten', 'twenty_five', 'fifty', 'seventy_five', 'ninety']
    rh = {}
    for site in rgb_rh:
        rh = create_plotlines(site, rh, percentiles, percentile_keys)
        plt.rc('ytick', labelsize=9) 
        plt.subplot(1,1,1)
        name = site['name']
        # make plot
        # plt.title('{}'.format(name), size=9)
        plt.xticks([])
        plt.tick_params(axis='y', which='major', pad=1)

        x = np.arange(0,366,1)
        month_ticks = [0,32,60,91,121,152,182,213,244,274,305,335]
        month_labels = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        plt.xticks(month_ticks, month_labels)
        plt.ylabel('Flow (cfs)', fontsize=10)
        # ax = plt.plot(rh['twenty_five'], color = 'white', alpha=1)
        plotlin = pd.to_numeric(site['data']['2006'], errors='coerce')
        plt.plot(plotlin)
        plt.savefig('nat_FQ.png')
        # import pdb; pdb.set_trace()
        plt.plot(rh['fifty'], color='#3d49f5', label = "50%")
        # plt.plot(rh['seventy_five'], color = 'white', alpha=1)
        plt.fill_between(x, rh['twenty_five'], rh['fifty'], color='#3d49f5', alpha = 0.6)
        plt.fill_between(x, rh['fifty'], rh['seventy_five'], color='#3d49f5', alpha = 0.6)

        # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=7, borderaxespad = .9, fontsize='small', labelspacing=.2, columnspacing=1, markerscale=.5)
        plt.title(site['name'])  
        plt.savefig('data_outputs/RGB_observed_rh/'+site['name']+'.png')  
        plt.clf()
    
def overlap_plots(rh_nat, rh_obs):
    percentiles = [25, 50, 75]
    percentile_keys = ['twenty_five', 'fifty', 'seventy_five']

    plotlines_nat = {}
    plotlines_obs = {}
    for index, site in enumerate(rh_nat):
        plotlines_nat = create_plotlines(rh_nat[index], plotlines_nat, percentiles, percentile_keys)
        plotlines_obs = create_plotlines(rh_obs[index], plotlines_obs, percentiles, percentile_keys)
        plt.rc('ytick', labelsize=16) 
        plt.subplot(1,1,1)
        name = site['name']
        plt.xticks([])
        plt.tick_params(axis='y', which='major', pad=1)

        x = np.arange(0,366,1)
        month_ticks = [0,32,60,91,121,152,182,213,244,274,305,335]
        month_labels = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        plt.xticks(month_ticks, month_labels, fontsize=16)
        plt.ylabel('Flow (cfs)', fontsize=10)
        ax = plt.gca()
        ax.set_ylim(0,12000)
        def plot_stuff(plotlines, color, plot_label):
            plt.plot(plotlines['fifty'], color=color, label = plot_label)
            plt.fill_between(x, plotlines['twenty_five'], plotlines['fifty'], color=color, alpha = 0.3)
            plt.fill_between(x, plotlines['fifty'], plotlines['seventy_five'], color=color, alpha = 0.3)
        plot = plot_stuff(plotlines_nat, '#3d49f5', 'Naturalized')
        plot = plot_stuff(plotlines_obs, '#D70040', 'Observed')
        # plt.legend(loc='upper right', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=7, borderaxespad = .9, fontsize='small', labelspacing=.2, columnspacing=1, markerscale=.5)
        plt.title(site['name'])  
        plt.savefig('data_outputs/RGB_overlaid_rh/'+site['name']+'.png', dpi=600)  
        plt.clf()
        # import pdb; pdb.set_trace()

    return