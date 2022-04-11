from os import rename
import numpy as np
import pandas as pd
from utils import import_ffc_data
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# Provide time period for observed metrics
# ('1990-2020', 14, 46), ('all', 0, 46), ('1995-2020', 19, 46), ('1990-2015', 14, 40), ('1985-2010', 9, 35), ('1980-2005', 4, 30), ('1975-2000', 0,25)
por = ('1990-2020', 14, 46)

# assemble data: ff metrics for all sites, observed and naturalized
data_folder = 'RGB_observed_ffc_outputs'
ffc_obs = import_ffc_data(data_folder, por[1], por[2])

data_folder = 'RGB_naturalized_ffc_outputs'
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

    ffc_obs[index]['ffc_metrics'] = ffc_obs[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')

    site_id = site['gage_id']
    metrics = site['ffc_metrics'].index
    range_50_perc_ls = []
    range_80_perc_ls = []
    final_scores = []
    percent_change = []
    naturalized_avg = []
    observed_avg = []
    designation_ls = []
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
        if obs_len == 0: # If a metric's values are all NA, easiest fix is to pass over them
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
        range_50_perc = (range_50/obs_len)*(1/.5) # multiplier accounts for limited range of naturalized vals in comparison
        range_80_perc = (range_80/obs_len)*(1/.8)
        if range_50_perc > 1: # set 1 as highest value possible
            range_50_perc = 1
        if range_80_perc > 1:
            range_80_perc = 1
        range_50_perc_ls.append(range_50_perc)
        range_80_perc_ls.append(range_80_perc)
        final_score = np.nanmean([range_50_perc, range_80_perc])
        # convert final score into a 0-100% score
        report_score = final_score * 100
        final_scores.append(report_score)
        # Assign letter grade and exceedance level based on 50th/80th scores
        # Scores: Excellent: 80th 0.8-0.55 and 50th 0.5-0.4: 
        # Good: 80th 0.4-0.8 and 50th 0.25-0.5
        # Extremely altered: 80th 0.15-0.4 and 50th 0.15-0.25
        # Severe danger: 80th 0-0.15 and 50th 0-0.15
        # Special concern - if none of other conditions have been met (should be 80th 0.4-0.8 OR 50th 0.25-0.5)

        score = None
        grade = None
        def get_scores(report_score):
            if report_score >= 100: 
                score = 'Very Good'
                grade = 'A+'
            elif 95 <= report_score < 100:
                score = 'Good'
                grade = 'A+'
            elif 85 <= report_score < 95:
                score = 'Good'
                grade = 'A'
            elif 80 <= report_score < 85:
                score = 'Good'
                grade = 'A-'
            elif 75 <= report_score < 80:
                score = 'Moderately Good'
                grade = 'B+'
            elif 65 <= report_score < 75:
                score = 'Moderately Good'
                grade = 'B'
            elif 60 <= report_score < 65:
                score = 'Moderately good'
                grade = 'B-'
            elif 55 <= report_score < 60:
                score = 'Moderate'
                grade = 'C+'
            elif 45 <= report_score < 55:
                score = 'Moderate'
                grade = 'C'
            elif 40 <= report_score < 45:
                score = 'Moderately Poor'
                grade = 'C-'
            elif 35 <= report_score < 40:
                score = 'Poor'
                grade = 'D+'
            elif 25 <= report_score < 35:
                score = 'Poor'
                grade = 'D'
            elif 20 <= report_score < 25:
                score = 'Poor'
                grade = 'D-'
            elif report_score < 20:
                score = 'Very poor'
                grade = 'F'
            return score, grade
        score, grade = get_scores(report_score)
        designation_ls.append(score)
        grade_ls.append(grade)
    
    output = pd.DataFrame(zip(range_50_perc_ls, range_80_perc_ls, final_scores, designation_ls, grade_ls), 
    columns = ['Interquartile', 'Interdecile', 'Final score', 'designation', 'grade'])
    # to print outputs individually for each site
    output['metrics'] = metrics
    output = output.set_index(['metrics'])
    output.to_csv('data_outputs/Alteration_scores_{}/{}.csv'.format(por[0], print_name))
    output = output.drop(['designation', 'grade', 'Interquartile', 'Interdecile'], axis=1)
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
    spring = site['alt_scores'].iloc[np.r_[0:4,8], :].mean()
    monsoon = site['alt_scores'].iloc[4:8,:].mean()
    dry = site['alt_scores'].iloc[9:13,:].mean()
    annual = site['alt_scores'].iloc[13:16,:].mean()
    components = pd.concat([spring, monsoon,  dry, annual], axis=1)
    components.columns = ['Spring Flood Pulse', 'Monsoon', 'Dry season', 'Annual']
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
def rename_cols(df):
    df = df.rename({'Final score': 'Alteration score'}, axis='columns')
    return df
upper_co = rename_cols(upper_co)
upper_nm = rename_cols(upper_nm)
middle = rename_cols(middle)
lower = rename_cols(lower)

all_sites = pd.concat(site_component_dfs).groupby(level=0, sort=False).mean() # arithmetic average all sites
all_sites = rename_cols(all_sites)

sites = [all_sites, upper_co, upper_nm, middle, lower]
for site in sites:
    grade_ls = []
    designation_ls = []
    for val in site['Alteration score']:
        designation, grade = get_scores(val)
        designation_ls.append(designation)
        grade_ls.append(grade)
    site['Grade'] = grade_ls
    site['Designation'] = designation_ls

all_sites.to_csv('data_outputs/Alteration_scores_{}/Report_card_regionalized_score.csv'.format(por[0]))
upper_co.to_csv('data_outputs/Alteration_scores_{}/Report_card_upper_co.csv'.format(por[0]))
upper_nm.to_csv('data_outputs/Alteration_scores_{}/Report_card_upper_nm.csv'.format(por[0]))
middle.to_csv('data_outputs/Alteration_scores_{}/Report_card_middle.csv'.format(por[0]))
lower.to_csv('data_outputs/Alteration_scores_{}/Report_card_lower.csv'.format(por[0]))
import pdb; pdb.set_trace()
# outputs: 1. Scores sorted by each ff component (and metric), qualitative score and letter grade, overall score
# 2. boxplot of values for each site's 4 components categories. Try to make output file with 4 plots in one  

for index, site in enumerate(ffc_obs):
    nat_data = ffc_nat[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    obs_data = ffc_obs[index]['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
    spring_metrics = {'name': 'Spring', 'all_metrics':['SP_Mag_50', 'SP_Tim', 'SP_Dur', 'SP_Mag_peak', 'SP_ROC'], 'mag_metrics':['SP_Mag_50', 'SP_Mag_peak'], 'nonmag_metrics':['SP_Tim', 'SP_Dur', 'SP_ROC']}
    monsoon_metrics = {'name': 'Monsoon', 'all_metrics':['Mons_mag_50', 'Mons_mag_90', 'Mons_Tim', 'Mons_Dur'], 'mag_metrics':['Mons_mag_50', 'Mons_mag_90'], 'nonmag_metrics':['Mons_Tim', 'Mons_Dur']}
    dry_metrics = {'name': 'Dry', 'all_metrics':['DS_Mag_50', 'DS_Mag_90', 'DS_Tim', 'DS_Dur_WS'], 'mag_metrics':['DS_Mag_50', 'DS_Mag_90'], 'nonmag_metrics':['DS_Tim', 'DS_Dur_WS']}
    annual_metrics = {'name': 'Annual', 'all_metrics':['Avg', 'CV'], 'mag_metrics':['Avg'], 'nonmag_metrics':['CV']}
    component_dicts = [spring_metrics, monsoon_metrics, dry_metrics, annual_metrics]
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
        sns.boxplot(ax=axes[0], data = boxplot_df1, x = 'metric', y='value', hue = 'condition', whis=[10, 90])
        sns.boxplot(ax=axes[1], data = boxplot_df2, x = 'metric', y='value', hue = 'condition', whis=[10, 90])
        plt.legend([],[], frameon=False) # remove second instance of legend
        # plt.suptitle('{} {} Metrics'.format(print_name, component['name']))
        plt.suptitle('{} Metrics'.format(component['name']))
        plt.savefig('data_outputs/Eco_exceedance_boxplots/{}/boxplot_{}.jpeg'.format(print_name, component['name']), dpi=600, bbox_inches='tight')
        # import pdb; pdb.set_trace()

