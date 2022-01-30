import numpy as np
import pandas as pd
from utils import import_ffc_data

# determine eco exceedance score for RGB observed flow data. Try w all ff metrics

# assemble data: ff metrics for all sites, observed and naturalized
data_folder = 'RGB_observed_ffc_outputs'
ffc_obs = import_ffc_data(data_folder)

data_folder = 'RGB_unimp_ffc_outputs_jan'
ffc_nat = import_ffc_data(data_folder)

site_dfs = [] # append each final df for a site to this list, take average over sites later
# for each site:
for index, site in enumerate(ffc_obs):
    ffc_nat[index]['ffc_metrics'] = ffc_nat[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    ffc_obs[index]['ffc_metrics'] = ffc_obs[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    site_id = site['gage_id']
    metrics = site['ffc_metrics'].index
    exceedance_freq = []
    percent_change = []
    naturalized_avg = []
    observed_avg = []
    for metric in metrics:
        # determine control bounds 'box' made by full range naturalized data
        control_min = min(ffc_nat[index]['ffc_metrics'].loc[metric])
        control_max = max(ffc_nat[index]['ffc_metrics'].loc[metric])
        exceedances = 0
        obs_metrics = ffc_obs[index]['ffc_metrics'].loc[metric]
        # determine frequency that observed flows exceed that metric's control values 
        for obs_metric in obs_metrics:
            if obs_metric < control_min or obs_metric > control_max:
                exceedances += 1
        exceedance_perc = exceedances/len(obs_metrics) * 100
        exceedance_freq.append(exceedance_perc)
        metric_obs = np.nanmean(obs_metrics)
        metric_nat = np.nanmean(ffc_nat[index]['ffc_metrics'].loc[metric])
        perc_change = (metric_nat - metric_obs)/metric_nat * 100
        percent_change.append(perc_change)
        naturalized_avg.append(metric_nat)
        observed_avg.append(metric_obs)
    output = pd.DataFrame(zip(exceedance_freq, percent_change, naturalized_avg, observed_avg), 
    columns = ['exceedance_freq', 'percent_change', 'naturalized_avg', 'observed_avg'])
    # to print outputs individually for each site
    output['metrics'] = metrics
    output = output.set_index(['metrics'])
    output.to_csv('data_outputs/Eco_exceedance_by_site/{}.csv'.format(site['gage_id']))

    site_dfs.append(output)
df_output = pd.concat(site_dfs).groupby(level=0, sort=False).mean()
df_output['metrics'] = metrics
df_output = df_output.set_index(['metrics'])
df_output.to_csv('data_outputs/Eco-exceedance_indicators.csv')

# Create outputs by component
df_output = df_output.drop(['naturalized_avg', 'observed_avg'], axis=1)
fall = df_output.iloc[0:3,:].mean()
wet = df_output.iloc[3:7,:].mean()
peak = df_output.iloc[7:16,:].mean()
spring = df_output.iloc[16:20,:].mean()
dry = df_output.iloc[20:24,:].mean()
annual = df_output.iloc[[24, 26, 27],:].mean()


components = pd.concat([fall, wet, peak, spring, dry, annual], axis=1)
components.columns = ['Fall pulse', 'Wet season', 'Peak flows', 'Spring recession', 'Dry season', 'Annual']
components = components.transpose()
components.to_csv('data_outputs/Eco_exceedance_components.csv')
# import pdb; pdb.set_trace()