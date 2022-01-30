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
    range_50_perc_ls = []
    range_80_perc_ls = []
    percent_change = []
    naturalized_avg = []
    observed_avg = []
    score_ls = []
    for metric in metrics:
        # determine bounds of 50th and 80th percentile
        lower_50 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.25)
        upper_50 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.75)
        lower_80 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.10)
        upper_80 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.90)

        range_50 = 0
        range_80 = 0
        obs_metrics = ffc_obs[index]['ffc_metrics'].loc[metric]
        # determine % values within range in each category
        # Double-check with Sam: are observed values to test agains naturalized supposed to be All the values (like I've done)?
        # Or should I be testing observed interquartile with the naturzlied interquartile?
        for obs_metric in obs_metrics:
            if obs_metric > lower_50 and obs_metric < upper_50:
                range_50 += 1
        for obs_metric in obs_metrics:
            if obs_metric > lower_80 and obs_metric < upper_80:
                range_80 += 1

        range_50_perc = range_50/len(obs_metrics)
        range_80_perc = range_80/len(obs_metrics)
        range_50_perc_ls.append(range_50_perc)
        range_80_perc_ls.append(range_80_perc)
        # Assign letter grade and exceedance level based on 50th/80th scores
        # Scores: Excellent: 80th 0.8-0.55 and 50th 0.5-0.4: 
        # Good: 80th 0.4-0.8 and 50th 0.25-0.5
        # In danger: 80th 0.15-0.4 and 50th 0.15-0.25
        # Extremely altered: 80th 0-0.15 and 50th 0-0.15
        # Special concern - if none of other conditions have been met (should be 80th 0.4-0.8 OR 50th 0.25-0.5)
        score = None
        if range_80_perc >= 0.55 and range_50_perc >= 0.4:
            score = 'Excellent'
        elif range_80_perc >= 0.4 and range_50_perc >= 0.25:
            score = 'Good'
        elif range_80_perc <= 0.15 and range_50_perc <= 0.15:
            score = 'Extremely altered'
        elif range_80_perc <= 0.4 and range_50_perc <= 0.25:
            score = 'In danger'
        else:
            score = 'Special concern'
        score_ls.append(score)

    output = pd.DataFrame(zip(range_50_perc_ls, range_80_perc_ls, score_ls), 
    columns = ['range_50_freq', 'range_80_freq', 'score'])
    # to print outputs individually for each site
    output['metrics'] = metrics
    output = output.set_index(['metrics'])
    output.to_csv('data_outputs/Eco_exceedance_score_by_site/{}.csv'.format(site['gage_id']))
    output = output.drop('score', axis=1)
    site_dfs.append(output)

df_output = pd.concat(site_dfs).groupby(level=0, sort=False).mean()
df_output['metrics'] = metrics
df_output = df_output.set_index(['metrics'])
df_output.to_csv('data_outputs/Eco-exceedance_score_Sam.csv')

# Create outputs by component
fall = df_output.iloc[0:3,:].mean()
wet = df_output.iloc[3:7,:].mean()
peak = df_output.iloc[7:16,:].mean()
spring = df_output.iloc[16:20,:].mean()
dry = df_output.iloc[20:24,:].mean()
annual = df_output.iloc[[24, 26, 27],:].mean()


components = pd.concat([fall, wet, peak, spring, dry, annual], axis=1)
components.columns = ['Fall pulse', 'Wet season', 'Peak flows', 'Spring recession', 'Dry season', 'Annual']
components = components.transpose()
import pdb; pdb.set_trace()
components.to_csv('data_outputs/Eco_exceedance_components_score_Sam.csv')
# import pdb; pdb.set_trace()

# outputs: 1. Scores sorted by each ff component (and metric), qualitative score and letter grade, overall score
# 2. boxplot of values for each site's 4 components categories. Try to make output file with 4 plots in one    