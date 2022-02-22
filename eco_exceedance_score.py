from os import rename
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

data_folder = 'RGB_unimp_ffc_outputs'
ffc_nat = import_ffc_data(data_folder)

site_dfs = [] # append each final df for a site to this list, take average over sites later
# for each site:
for index, site in enumerate(ffc_obs):
    names_dict = {'RG6_':'RG6_NR_LOBATOS', 'RG7_':'RG7_NR_CERRO', 'RG8_':'RG8_NR_TAOS_BRIDGE', 'RG9_':'RG9_EMBUDO', 'RG10':'RG10_OTOWI_BRIDGE',
    'RG11':'RG11_BLW_COCHITI_DAM', 'RG12':'RG12_SAN_FELIPE', 'RG14':'RG14_ALBUQUERQUE', 'RG15':'RG15_AT_SAN_MARCIAL', 'RG16':'RG16_NR_SAN_ACACIA',
    'RG18':'RG18_BLW_ELEPHANT_BUTTE', 'RG19':'RG19_BLW_CABALLO', 'RG20':'RG20_EL_PASO', 'RG21':'RG21_FORT_QUITMAN', 'RG22':'RG22_ABV_RIO_CONCHOS'}
    for site_name in names_dict.keys():
            if site_name == site['gage_id']:
                print_name = names_dict[site_name]

    ffc_nat[index]['ffc_metrics'] = ffc_nat[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    ffc_nat[index]['ffc_metrics'] = ffc_nat[index]['ffc_metrics'].drop(['Peak_2','Peak_5','Peak_10','Peak_Dur_2',
    'Peak_Dur_5','Peak_Dur_10','Peak_Fre_2','Peak_Fre_5', 'Peak_Fre_10','Std','DS_No_Flow'], axis=0)

    ffc_obs[index]['ffc_metrics'] = ffc_obs[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    ffc_obs[index]['ffc_metrics'] = ffc_obs[index]['ffc_metrics'].drop(['Peak_2','Peak_5','Peak_10','Peak_Dur_2',
    'Peak_Dur_5','Peak_Dur_10','Peak_Fre_2','Peak_Fre_5', 'Peak_Fre_10','Std','DS_No_Flow'], axis=0)

    site_id = site['gage_id']
    metrics = site['ffc_metrics'].index
    range_50_perc_ls = []
    range_80_perc_ls = []
    final_scores = []
    percent_change = []
    naturalized_avg = []
    observed_avg = []
    score_ls = []
    grade_ls = []
    for metric in metrics:
        # determine bounds of 50th and 80th percentile
        lower_50 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.25)
        upper_50 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.75)
        lower_80 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.10)
        upper_80 = np.nanquantile(ffc_nat[index]['ffc_metrics'].loc[metric], 0.90)

        range_50 = 0
        range_80 = 0
        obs_metrics = ffc_obs[index]['ffc_metrics'].loc[metric]
        obs_len = len(obs_metrics.dropna())
        if obs_len == 0: # some peak metrics are all NA, easiest fix is to pass over them
            continue
        # determine % values within range in each category
        # Double-check with Sam: are observed values to test agains naturalized supposed to be All the values (like I've done)?
        # Or should I be testing observed interquartile with the naturzlied interquartile?
        for obs_metric in obs_metrics:
            if obs_metric >= lower_50 and obs_metric <= upper_50:
                range_50 += 1
        for obs_metric in obs_metrics:
            if obs_metric >= lower_80 and obs_metric <= upper_80:
                range_80 += 1
        range_50_perc = range_50/obs_len
        range_80_perc = range_80/obs_len
        range_50_perc_ls.append(range_50_perc)
        range_80_perc_ls.append(range_80_perc)
        final_score = np.nanmean([range_50_perc, range_80_perc])
        
        # convert final score into a 0-100% score
        report_score = None 
        if final_score > 0.5:
            report_score = 100
        else: 
            report_score = final_score * 200
        final_scores.append(report_score)
        # Assign letter grade and exceedance level based on 50th/80th scores
        # Scores: Excellent: 80th 0.8-0.55 and 50th 0.5-0.4: 
        # Good: 80th 0.4-0.8 and 50th 0.25-0.5
        # Extremely altered: 80th 0.15-0.4 and 50th 0.15-0.25
        # Severe danger: 80th 0-0.15 and 50th 0-0.15
        # Special concern - if none of other conditions have been met (should be 80th 0.4-0.8 OR 50th 0.25-0.5)
        score = None
        grade = None
        scoring_strategy = 'one-value'
        # scoring_strategy = 'two-value'
        if scoring_strategy == 'two-value':
            if range_80_perc >= 0.55 and range_50_perc >= 0.4:
                score = 'Excellent'
                grade = 'A'
            elif range_80_perc >= 0.4 and range_50_perc >= 0.25:
                score = 'Good'
                grade = 'B'
            elif range_80_perc <= 0.15 and range_50_perc <= 0.15:
                score = 'Severe danger'
                grade = 'F'
            elif range_80_perc <= 0.4 and range_50_perc <= 0.25:
                score = 'Extremely altered'
                grade = 'D'
            else:
                score = 'Special concern'
                grade = 'C'
            score_ls.append(score)
            grade_ls.append(grade)
        elif scoring_strategy == 'one-value':
            if report_score >= 100: 
                score = 'Excellent'
                grade = 'A'
            elif 80 <= report_score <= 100:
                score = 'Good'
                grade = 'B'
            elif 60 <= report_score <= 80:
                score = 'Moderately good'
                grade = 'C+'
            elif 40 <= report_score <= 60:
                score = 'Moderate'
                grade = 'C-'
            elif 20 <= report_score <= 40:
                score = 'Poor'
                grade = 'D'
            elif report_score <= 20:
                score = 'Very poor'
                grade = 'F'
            score_ls.append(score)
            grade_ls.append(grade)
    
    output = pd.DataFrame(zip(range_50_perc_ls, range_80_perc_ls, final_scores, score_ls, grade_ls), 
    columns = ['Interquartile', 'Interdecile', 'Final score', 'designation', 'grade'])
    # to print outputs individually for each site
    output['metrics'] = metrics
    output = output.set_index(['metrics'])
    output.to_csv('data_outputs/Alteration_scores/{}.csv'.format(print_name))
    output = output.drop(['designation', 'grade'], axis=1)
    site['alt_scores'] = output
    site_dfs.append(output)

# Aggregation: geom average of all metrics per component. Arithmetic avg across all sites' components. 
# And finally: arithmetic mean of regionalized components for one final number. 
site_component_dfs = []
# average components by basin reaches, too
upper_co = []
upper_nm = []
middle = []
lower = []
for site in ffc_obs:
    # Create outputs by component
    fall = pd.Series(stats.gmean(site['alt_scores'].iloc[0:3,:]))
    wet = pd.Series(stats.gmean(site['alt_scores'].iloc[3:7,:]))
    spring = pd.Series(stats.gmean(site['alt_scores'].iloc[7:11,:]))
    dry = pd.Series(stats.gmean(site['alt_scores'].iloc[11:15,:]))
    annual = pd.Series(stats.gmean(site['alt_scores'].iloc[15:17,:]))
    components = pd.concat([fall, wet, spring, dry, annual], axis=1)
    components.columns = ['Fall pulse', 'Wet season', 'Spring recession', 'Dry season', 'Annual']
    components = components.transpose()
    site_component_dfs.append(components)
    if site['gage_id'] == 'RG6_':
        upper_co.append(components)
    elif site['gage_id'] == 'RG7_' or site['gage_id'] == 'RG8_' or site['gage_id'] == 'RG9_' or site['gage_id'] == 'RG10':
        upper_nm.append(components)
    elif site['gage_id'] == 'RG11' or site['gage_id'] == 'RG12' or site['gage_id'] == 'RG14' or site['gage_id'] == 'RG15' or \
    site['gage_id'] == 'RG16' or site['gage_id'] == 'RG18':
        middle.append(components)
    elif site['gage_id'] == 'RG19' or site['gage_id'] == 'RG20' or site['gage_id'] == 'RG21':
        lower.append(components)
# Take regional arithmetic averages of site totals
upper_co = pd.concat(upper_co).groupby(level=0, sort=False).mean()
upper_nm = pd.concat(upper_nm).groupby(level=0, sort=False).mean()
middle = pd.concat(middle).groupby(level=0, sort=False).mean()
lower = pd.concat(lower).groupby(level=0, sort=False).mean()
# import pdb; pdb.set_trace()

def rename_cols(df):
    df = df.rename(columns={0: 'Interquartile', 1: 'Interdecile'})
    return df
upper_co = rename_cols(upper_co)
upper_nm = rename_cols(upper_nm)
middle = rename_cols(middle)
lower = rename_cols(lower)

all_sites = pd.concat(site_component_dfs).groupby(level=0, sort=False).mean() # arithmetic average all sites
all_sites = rename_cols(all_sites)

all_sites.to_csv('data_outputs/Alteration_scores/Eco-exceedance_regionalized_score_Sam.csv')
upper_co.to_csv('data_outputs/Alteration_scores/Eco-exceedance_upper_co.csv')
upper_nm.to_csv('data_outputs/Alteration_scores/Eco-exceedance_upper_nm.csv')
middle.to_csv('data_outputs/Alteration_scores/Eco-exceedance_middle.csv')
lower.to_csv('data_outputs/Alteration_scores/Eco-exceedance_lower.csv')
import pdb; pdb.set_trace()
# outputs: 1. Scores sorted by each ff component (and metric), qualitative score and letter grade, overall score
# 2. boxplot of values for each site's 4 components categories. Try to make output file with 4 plots in one  

for index, site in enumerate(ffc_obs):
    # import pdb; pdb.set_trace()
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

    names_dict = {'RG6_':'RG6_NR_LOBATOS', 'RG7_':'RG7_NR_CERRO', 'RG8_':'RG8_NR_TAOS_BRIDGE', 'RG9_':'RG9_EMBUDO', 'RG10':'RG10_OTOWI_BRIDGE',
    'RG11':'RG11_BLW_COCHITI_DAM', 'RG12':'RG12_SAN_FELIPE', 'RG14':'RG14_ALBUQUERQUE', 'RG15':'RG15_AT_SAN_MARCIAL', 'RG16':'RG16_NR_SAN_ACACIA',
    'RG18':'RG18_BLW_ELEPHANT_BUTTE', 'RG19':'RG19_BLW_CABALLO', 'RG20':'RG20_EL_PASO', 'RG21':'RG21_FORT_QUITMAN', 'RG22':'RG22_ABV_RIO_CONCHOS'}
    for site_name in names_dict.keys():
            if site_name == site['gage_id']:
                print_name = names_dict[site_name]

    for component in component_dicts:
        fig, axes = plt.subplots(1, 2, figsize=(10,6))
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
        plt.suptitle('{} {} Metrics'.format(print_name, component['name']))
        plt.savefig('data_outputs/Eco_exceedance_boxplots/{}/boxplot_{}.jpeg'.format(print_name, component['name']), dpi=600, bbox_inches='tight')
        # import pdb; pdb.set_trace()

