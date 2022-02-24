# Keep useful misc functions here
import glob
import pandas as pd
import numpy as np
from datetime import datetime

def import_drh_data(data_folder):
    drh_files = glob.glob('data_inputs/{}/*drh.csv'.format(data_folder)) 
    drh_dicts = []
    for index, drh_file in enumerate(drh_files):
        drh_dict = {}
        drh_dict['name'] = drh_file.split('/')[2][:-8]
        drh_dict['data'] = pd.read_csv(drh_file, sep=',', index_col=0, header=None)
        drh_dicts.append(drh_dict)
    rh_files = glob.glob('data_inputs/{}/*matrix.csv'.format(data_folder))
    rh_dicts = []
    for index, rh_file in enumerate(rh_files):
        rh_dict = {} 
        rh_dict['name'] = rh_file.split('/')[2][:-23] 
        rh_dict['data'] = pd.read_csv(rh_file, sep=',', index_col=None)
        rh_dicts.append(rh_dict)
    return drh_dicts, rh_dicts

def import_ffc_data(data_folder, date_start=0, date_end=46):
    folder = 'data_inputs/{}'.format(data_folder)
    main_metric_files = glob.glob(folder + '/*flow_result.csv')
    supp_metric_files = glob.glob(folder + '/*supplementary_metrics.csv')
    ffc_dicts = []
    supp_dicts = []
    for supp_file in supp_metric_files:
        supp_dict = {}
        supp_dict['gage_id'] = supp_file.split('/')[2][0:4] 
        supp_dict['supp_metrics'] = pd.read_csv(supp_file, sep=',', index_col=0)
        # to reduce POR: [all] 0:46, [1995-2021] 19:46, [1990-2015] 14:40, [1985-2010] 9:35, [1980-2005] 4:30, [1975-2000] 0:25
        if data_folder == 'RGB_observed_ffc_outputs':
            supp_dict['supp_metrics'] = supp_dict['supp_metrics'].iloc[:,date_start:date_end]
        supp_dicts.append(supp_dict)
    for metric_file in main_metric_files:
        main_metrics = pd.read_csv(metric_file, sep=',', index_col=0)
        # to reduce POR:
        if data_folder == 'RGB_observed_ffc_outputs':
            main_metrics = main_metrics.iloc[:,date_start:date_end]
        main_dict = {}
        main_dict['gage_id'] = metric_file.split('/')[2][0:4] 
        # align supplemental metric file with main metric file, and add info to the main gage dict
        for supp_dict in supp_dicts:
            if supp_dict['gage_id'] == main_dict['gage_id']:
                main_dict['ffc_metrics'] = pd.concat([main_metrics, supp_dict['supp_metrics']], axis=0)
        ffc_dicts.append(main_dict)
    return ffc_dicts

def summarize_ffc_metrics(data_folder, flow_condition):
    ffc_dicts = import_ffc_data(data_folder)  
    # Summarize metrics across years in [median and percentiles]
    for ffc_dict in ffc_dicts:
        ffc_dict['ffc_metrics'] = ffc_dict['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
        ffc_dict['ffc_metrics'] = ffc_dict['ffc_metrics'].drop(['Std', 'DS_No_Flow'])
        sum_med = ffc_dict['ffc_metrics'].quantile(.5, axis=1)
        sum_10 = ffc_dict['ffc_metrics'].quantile(.10, axis=1)
        sum_25 = ffc_dict['ffc_metrics'].quantile(.25, axis=1)
        sum_75 = ffc_dict['ffc_metrics'].quantile(.75, axis=1)
        sum_90 = ffc_dict['ffc_metrics'].quantile(.90, axis=1)
        headers = ['tenth', 'twenty-fifth', 'fiftieth', 'seventy-fifth', 'nintieth']
        summary_output = pd.DataFrame(zip(sum_10, sum_25, sum_med, sum_75, sum_90), columns=headers, index=sum_med.index)
        names_dict = {'RG6_':'RG6_NR_LOBATOS', 'RG7_':'RG7_NR_CERRO', 'RG8_':'RG8_NR_TAOS_BRIDGE', 'RG9_':'RG9_EMBUDO', 'RG10':'RG10_OTOWI_BRIDGE',
        'RG11':'RG11_BLW_COCHITI_DAM', 'RG12':'RG12_SAN_FELIPE', 'RG14':'RG14_ALBUQUERQUE', 'RG15':'RG15_AT_SAN_MARCIAL', 'RG16':'RG16_NR_SAN_ACACIA',
        'RG18':'RG18_BLW_ELEPHANT_BUTTE', 'RG19':'RG19_BLW_CABALLO', 'RG20':'RG20_EL_PASO', 'RG21':'RG21_FORT_QUITMAN', 'RG22':'RG22_ABV_RIO_CONCHOS'}
        for site_name in names_dict.keys():
            if site_name == ffc_dict['gage_id']:
                print_name = names_dict[site_name]
        summary_output.to_csv('data_outputs/Metric_summaries_{}/{}.csv'.format(flow_condition, print_name))

def compile_data():
    data_cols = pd.read_csv('data_inputs/RGB_observed_daily_discharge.csv')
    dates = data_cols['date']
    new_date_col = pd.Series(np.empty(len(dates)))
    for index, row in enumerate(dates):
        date_obj = datetime.strptime(dates[index], '%m/%d/%y')
        new_date_col[index] = date_obj.strftime('%m/%d/%Y')
    flow_cols = data_cols.iloc[:,1:]
    for index, flow_col in enumerate(flow_cols):
        name = flow_cols.iloc[:,index].name
        output = pd.DataFrame(zip(new_date_col, flow_cols.iloc[:,index]), columns = ['date', 'flow'])
        output.to_csv('data_inputs/RGB_observed_ffc_inputs/'+name+'.csv', index=None)

def convert_15_min():
    files_15_cms = glob.glob('data_inputs/RGB_15_min_cms/*.csv')
    for flow_15 in files_15_cms:
        name = flow_15.split('/')[2][:-4]
        flow_data_15 = pd.read_csv(flow_15)
        # create dict of empty ordered daily entries
        data_by_date = {}
        dates_pd = pd.to_datetime(flow_data_15['date'])
        date_range = pd.date_range(dates_pd[0], dates_pd.iloc[-1])
        for date in date_range:
            data_by_date[date] = []
        # populate dict entries with array of flow values for each date
        for index, row in flow_data_15.iterrows():
            date = dates_pd[index]
            try: # convert flow values to float, if possible
                data_by_date[date].append(np.float(row['flow']))
            except: # Nan vals may not be convertible
                data_by_date[date].append(row['flow'])
        flow_avg = []
        for index, date in enumerate(date_range):
            flow_avg.append(np.nanmean(data_by_date[date]))
        daily_output = pd.DataFrame(list(zip(date_range,flow_avg)),columns =['date','flow'])
        daily_output.to_csv(name + '_daily.csv', index=False, )