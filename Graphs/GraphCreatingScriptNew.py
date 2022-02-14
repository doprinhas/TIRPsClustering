import Globals as Glob
from DataParser import DataParser
import Graphs
import HelpFunctions as Functions
import itertools
import json
import numpy as np


def create_graph(output_dir, param_name, main_score, filter_params, suffix='', format='-o'):
    file_name, title = \
        f'{output_dir}{main_score}-{param_name}', f'Average Solutions {main_score} as a function\nof {param_name}'
    if suffix != '':
        file_name += f' -- {suffix}'; title += f' -- {suffix}'
    x, ys, errors, labels = dp.get_results_by_param_topcans_split(param_name, main_score, filter_params)
    Graphs.plot_multi_line_with_error_chart(file_name, x, ys, errors, labels, title, param_name, f'Average {main_score}', format)


def coverage_and_clusters_number_graph(output_dir, param_name, filter_params, suffix='', format='-o'):
    for g_score in ['Coverage', 'Number of Clusters']:
        file_name, title = \
            f'{output_dir}{g_score}-{param_name}', f'Average Solutions {g_score} as a function\nof {param_name}'
        if suffix != '':
            file_name += f' -- {suffix}'; title += f' -- {suffix}'
        x, ys, errors, labels = dp.get_results_by_param_topcans_split(param_name, g_score, filter_params)
        Graphs.plot_multi_line_with_error_chart(file_name, x, ys, errors, labels, title, param_name, g_score, format)


def create_param_graphs(param_name, filter_params=[], format='-o'):
    output_d = f'{output_dir}{param_name}/'
    Functions.create_directory(output_d)

    # filter_params = [('Stopping Criteria', [0.01, 0.05, 0.1]), ('Top Cans', [1, 5, 10])]

    create_graph(output_d, param_name, 'Score', filter_params, '', format)
    create_graph(output_d, param_name, 'Homogeneity', filter_params, '', format)
    create_graph(output_d, param_name, 'Extrapolation', filter_params, '', format)
    create_graph(output_d, param_name, 'Time', filter_params, '', format)
    coverage_and_clusters_number_graph(output_d, param_name, filter_params, param_name, format)


def create_scatter_graphs(scores):
    global Colors
    scores_lists = {key: [] for key in scores}
    for score_name, tirps_scores in scores.items():
        for tirp in sorted(tirps_scores):
            scores_lists[score_name].append(tirps_scores[tirp])

    tirps_sizes = [Functions.get_tirp_size(tirp) for tirp in sorted(tirps_scores)]

    output_d = f'{output_dir}Scatter Graphs/'
    Functions.create_directory(output_d)

    Graphs.plot_scatter_chart(f'{output_d}Score-VS', scores_lists['VS'], scores_lists['Score'], 'Score - VS', 'VS', 'Score', tirps_sizes)
    Graphs.plot_scatter_chart(f'{output_d}Homogeneity-VS', scores_lists['VS'], scores_lists['Mean Homogeneity'], 'Homogeneity - VS', 'VS', 'Homogeneity', tirps_sizes)
    Graphs.plot_scatter_chart(f'{output_d}Extrapolation-VS', scores_lists['VS'], scores_lists['Mean Extrapolation'], 'Extrapolation - VS', 'VS', 'Extrapolation', tirps_sizes)
    Graphs.plot_scatter_chart(f'{output_d}Homogeneity-Extrapolation', scores_lists['Mean Extrapolation'], scores_lists['Mean Homogeneity'], 'Homogeneity - Extrapolation', 'Extrapolation', 'Homogeneity', tirps_sizes)

    Graphs.plot_scatter_chart(f'{output_d}Average Combined Score-Multiply Combined Score', scores_lists['Old Score'],
                              scores_lists['Score'], 'Average Combined Score - Multiply Combined Score', 'Multiply Combined Score', 'Average Combined Score', tirps_sizes)
    Graphs.plot_scatter_chart(f'{output_d}Mean Extrapolation-Strict Extrapolation', scores_lists['Strict Extrapolation'],
                              scores_lists['Mean Extrapolation'], 'Mean Extrapolation - Strict Extrapolation', 'Strict Extrapolation', 'Mean Extrapolation', tirps_sizes)

def create_scores_tirp_size(scores):
    x_label = 'TIRPs Size'
    for score, scores_dic in scores.items():
        if score == 'VS' or score == 'Old Score' or score == 'Strict Extrapolation':
            continue
        x, ys, errors, labels = dp.get_results_by_param_initcans_split(x_label, score)
        labels.append('All')
        y, error = get_tirps_scores_by_size(x, scores_dic)
        ys.append(y); errors.append(error)
        Graphs.plot_multi_line_with_error_chart(f'{output_dir}{x_label}/{score}-{x_label} -- InitCans',
                                                x, ys, errors, labels, f'Average {score} as a function\nof {x_label}', x_label, f'Average {score}', 'o')


def get_tirps_scores_by_size(tirps_sizes, score_dic):
    global dp
    y, error = [], []
    all_tirps = list(score_dic.keys())
    for tirp_size in tirps_sizes:
        tirps = Functions.get_tirps_names_by_size(all_tirps, tirp_size)
        mean, ci = get_tirps_average_score_ci(tirps, score_dic)
        y.append(mean); error.append(ci)
    return y, error


def get_tirps_average_score_ci(tirps, score_dic, z=1.96):
    values = [score_dic[tirp] for tirp in tirps]
    mean, std = np.mean(values), np.std(values)
    return mean, std*z / np.sqrt(len(values))


def instance_to_graph(intervals, states):
    xs, ys = [], []
    for interval, state in zip(intervals, states):
        xs.append([interval[0], interval[1]])
        ys.append([state] * 2)
    return ys, xs


def get_score_dictionaries(dir_path):
    homo, extra, st_extra, old_scores = {}, {}, {}, {}
    homo_extra = json.load(open(f'{dir_path}homo&extra.json'))

    for tirp in homo_extra:
        homo[tirp], extra[tirp], st_extra[tirp], old_scores[tirp] = homo_extra[tirp]

    return {
        'Mean Homogeneity': homo,
        'Mean Extrapolation': extra,
        'Strict Extrapolation': st_extra,
        'Old Score': old_scores,
        'VS': json.load(open(f'{dir_path}VS.json')),
        'Score': json.load(open(f'{dir_path}scores.json'))
    }


params_names = ['Stopping Criteria', 'Initial Cans']  # 'Weights', 'Initial Cans', 'TIRPs Size', 'Stopping Criteria'

for dataset_name in ['deb_sax_3_1_10_7_60_True_Gender', 'icu_sax_3_1_20_7_30_True_Gender']:
    # dataset_name = 'SAHS_300_B_3-4_sax_3_1_30_7_10_True'
    output_dir = f'{Glob.Graphs_Dir_Path}{dataset_name}/'
    Functions.create_directory(output_dir)
    dp = DataParser(f'{Glob.Clusters_Results_Dir_Path}{dataset_name}')
    dp.parse_files()
    Functions.create_directory(output_dir)
    filter_params = []#[('Stopping Criteria', [0.01, 0.03, 0.05])]

    # create_param_graphs('TIRPs Size', filter_params, 'o')
    create_param_graphs('Initial Cans', filter_params, '-o')
    create_param_graphs('Stopping Criteria', filter_params, '-o')

    dataset_path = f'{Glob.KL_O_Dir_Path}{dataset_name.replace("_Gender", "")}/'
    scores = get_score_dictionaries(dataset_path)

    create_scatter_graphs(scores)
    # create_scores_tirp_size(scores)

    dp.results_df.to_csv(f'{output_dir}results.csv')
    print(f'{output_dir}results.csv')
    # break

# from TIRPFileParser import TIRPFileParser
# tirps_paths = dp.results_df['TIRPs'][990]
#
# tirps = []
# for t_p in tirps_paths:
#     tn = t_p.split('/')[-1]
#     # print(t_p)
#     tp = TIRPFileParser(t_p, t_p.replace(tn, 'states.csv'))
#     labels = tp.states_dis
#     ys, xs = instance_to_graph(tp.get_general_instance(), labels)
#     print(tp.get_general_instance())
#     Graphs.plot_multi_line_chart_TIRPS(xs, ys, labels, tp.dis)
#     # break







