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
    site_dfs.append(output)
df_output = pd.concat(site_dfs).groupby(level=0).mean()
df_output['metrics'] = metrics
df_output = df_output.set_index(['metrics'])
df_output.to_csv('data_outputs/Eco-exceedance_indicators.csv')
# import pdb; pdb.set_trace()