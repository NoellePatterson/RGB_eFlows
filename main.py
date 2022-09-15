# Main execution file for RBG work products
# Noelle Patterson, fall-winter 2021
from utils import import_drh_data, summarize_ffc_metrics, compile_data, convert_15_min
from visualize import plot_rh, overlap_plots

# output = compile_data()
# result = convert_15_min()

data_folder = 'Pecos_Reg'

drh_dicts_obs, rh_dicts_obs = import_drh_data(data_folder)
summarize_ffc_metrics(data_folder, 'observed')
import pdb; pdb.set_trace()

data_folder = 'RGB_naturalized_ffc_outputs'
# drh_dicts_nat, rh_dicts_nat = import_drh_data(data_folder)
# summarize_ffc_metrics(data_folder, 'naturalized')
# import pdb; pdb.set_trace()
# for plotting function, input dataset dicts and flow condition (observed/naturalized)
plot = plot_rh(rh_dicts_obs, 'naturalized') # naturalized or observed
# plot = overlap_plots(rh_dicts_nat, rh_dicts_obs)

