import numpy as np
import pandas as pd
from utils import import_ffc_data
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

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
    output.to_csv('data_outputs/Eco_exceedance_by_site_Sam/{}.csv'.format(site['gage_id']))
    output = output.drop('score', axis=1)
    site_dfs.append(output)
# Aggregation: geom average of all metrics per component. Arithmetic avg across all sites' components. 
# And finally: arithmetic mean of regionalized components for one final number. 
site_component_dfs = []
for site in site_dfs:
    # Create outputs by component
    fall = pd.Series(stats.gmean(site.iloc[0:3,:]))
    wet = pd.Series(stats.gmean(site.iloc[3:7,:]))
    peak = pd.Series(stats.gmean(site.iloc[7:16,:]))
    spring = pd.Series(stats.gmean(site.iloc[16:20,:]))
    dry = pd.Series(stats.gmean(site.iloc[20:24,:]))
    annual = pd.Series(stats.gmean(site.iloc[[24, 26, 27],:]))
    components = pd.concat([fall, wet, peak, spring, dry, annual], axis=1)
    components.columns = ['Fall pulse', 'Wet season', 'Peak flows', 'Spring recession', 'Dry season', 'Annual']
    components = components.transpose()
    site_component_dfs.append(components)

df_output = pd.concat(site_component_dfs).groupby(level=0, sort=False).mean()

df_output.to_csv('data_outputs/Eco-exceedance_regionalized_score_Sam.csv')
import pdb; pdb.set_trace()

# outputs: 1. Scores sorted by each ff component (and metric), qualitative score and letter grade, overall score
# 2. boxplot of values for each site's 4 components categories. Try to make output file with 4 plots in one    
for index, site in enumerate(ffc_obs):
    nat_data = ffc_nat[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    obs_data = ffc_obs[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')

    fall_metrics = {'name': 'Fall', 'all_metrics':['FA_Mag', 'FA_Tim', 'FA_Dur'], 'mag_metrics':['FA_Mag'], 'nonmag_metrics':['FA_Tim', 'FA_Dur']}
    wet_metrics = {'name': 'Wet', 'all_metrics':['Wet_BFL_Mag_10', 'Wet_BFL_Mag_50', 'Wet_Tim', 'Wet_BFL_Dur'], 'mag_metrics':['Wet_BFL_Mag_10', 'Wet_BFL_Mag_50'], 'nonmag_metrics':['Wet_Tim', 'Wet_BFL_Dur']}
    spring_metrics = {'name': 'Spring', 'all_metrics':['SP_Mag', 'SP_Tim', 'SP_Dur', 'SP_ROC'], 'mag_metrics':['SP_Mag'], 'nonmag_metrics':['SP_Tim', 'SP_Dur', 'SP_ROC']}
    dry_metrics = {'name': 'Dry', 'all_metrics':['DS_Mag_50', 'DS_Mag_90', 'DS_Tim', 'DS_Dur_WS'], 'mag_metrics':['DS_Mag_50', 'DS_Mag_90'], 'nonmag_metrics':['DS_Tim', 'DS_Dur_WS']}
    annual_metrics = {'name': 'Annual', 'all_metrics':['Avg', 'CV', 'DS_No_Flow'], 'mag_metrics':['Avg'], 'nonmag_metrics':['CV', 'DS_No_Flow']}
    component_dicts = [fall_metrics, wet_metrics, spring_metrics, dry_metrics, annual_metrics]
    # group each component's data into long format, w col for obs/nat condition 
    # plot magnitude separately bc values are so different
    
    for component in component_dicts:
        fig, axes = plt.subplots(1, 2, figsize=(8,6))
        fall_metrics_nat = nat_data.loc[component['all_metrics'], :]
        fall_metrics_nat = fall_metrics_nat.transpose()
        fall_metrics_nat['condition'] = ['naturalized']*len(fall_metrics_nat.index)
        fall_metrics_obs = obs_data.loc[component['all_metrics'], :]
        fall_metrics_obs = fall_metrics_obs.transpose()
        fall_metrics_obs['condition'] = ['observed']*len(fall_metrics_obs.index)
        frames = [fall_metrics_nat, fall_metrics_obs]
        boxplot_df = pd.concat(frames)
        boxplot_df1 = boxplot_df.drop(component['mag_metrics'], axis=1)
        boxplot_df1 = pd.melt(boxplot_df1, id_vars=['condition'], value_vars=component['nonmag_metrics'], var_name='metric')
        boxplot_df2 = boxplot_df.drop(component['nonmag_metrics'], axis=1)
        boxplot_df2 = pd.melt(boxplot_df2, id_vars=['condition'], value_vars=component['mag_metrics'], var_name='metric')
        sns.boxplot(ax=axes[0], data = boxplot_df1, x = 'metric', y='value', hue = 'condition')
        sns.boxplot(ax=axes[1], data = boxplot_df2, x = 'metric', y='value', hue = 'condition')
        plt.legend([],[], frameon=False) # remove second instance of legend
        plt.suptitle('{} Metrics'.format(component['name']))
        plt.savefig('data_outputs/Eco_exceedance_boxplots/{}/boxplot_{}.jpeg'.format(site['gage_id'], component['name']), dpi=600)
    # import pdb; pdb.set_trace()