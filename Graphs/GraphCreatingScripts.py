import Globals as Glob
from DataParser import DataParser
import Graphs
import HelpFunctions as Functions
import itertools


def weights_to_ticks(ws):
    ticks = []
    for w in ws:
        ticks.append(w[7:].replace('_', '\n'))
    return ticks


def create_graph(output_dir, param_name, main_score, filter_params, suffix):
    x, ys, labels = dp.get_results_by_param_topcans_split(param_name, main_score, filter_params)
    Graphs.plot_multi_line_chart(f'{output_dir}{main_score}-{param_name} -- {suffix}.png', x, ys, labels,
                                 f'{main_score}-{param_name} -- {suffix}', param_name, main_score)
    g_scores = ['Coverage', 'Number of Clusters']
    for g_score in g_scores:
        x, ys, labels = dp.get_results_by_param_topcans_split(param_name, g_score, filter_params)
        Graphs.plot_multi_line_chart(f'{output_dir}{g_score}-{param_name} -- {suffix}.png', x, ys, labels,
                                     f'{g_score}-{param_name} -- {suffix}', param_name, g_score)


def switch(l, i, j):
    l[i], l[j] = l[j], l[i]


def switch_ys(ys, i, j):
    for y in ys:
        switch(y, i, j)


def sort_weights(main_score, sec_score, x, ys):
    i = x.index(f'1-{main_score}')
    switch(x, i, 0)
    switch_ys(ys, i, 0)

    i = x.index(f'0.67-{main_score}\n0.33-{sec_score}') if f'0.67-{main_score}\n0.33-{sec_score}' in x else x.index(f'0.33-{sec_score}\n0.67-{main_score}')
    switch(x, i, 1)
    switch_ys(ys, i, 1)

    i = x.index(f'0.33-{main_score}\n0.67-{sec_score}') if f'0.67-{main_score}\n0.33-{sec_score}' in x else x.index(f'0.67-{sec_score}\n0.33-{main_score}')
    switch(x, i, 2)
    switch_ys(ys, i, 2)

    i = x.index(f'1-{sec_score}')
    switch(x, i, 3)
    switch_ys(ys, i, 3)



def create_weights_graph(output_dir, param_name, main_score, sec_score, filter_params, suffix):
    x, ys, labels = dp.get_results_by_param_topcans_split(param_name, main_score, filter_params)
    x = weights_to_ticks(x)
    sort_weights(main_score, sec_score, x, ys)
    Graphs.plot_multi_line_chart(f'{output_dir}{main_score}-{param_name} -- {suffix}.png', x, ys, labels,
                                 f'{main_score}-{param_name} -- {suffix}', param_name, main_score)


def create_param_graphs_split_by_initial_cans(param_name):
    output_d = f'{output_dir}{param_name}/'
    Functions.create_directory(output_d)
    scores = ['Gender', 'Age', 'BMI']

    filter_params = [('Initial Cans', [30]), ('Weights', ['1-Inter'])]
    suffix = '30-Intersection'
    create_graph(output_d, param_name, 'Intersection', filter_params, suffix)
    for m_score in scores:
        filter_params = [('Initial Cans', [30]), ('Weights', [f'1-Homo_1-{m_score}'])]
        suffix = f'30-{m_score}'
        create_graph(output_d, param_name, m_score, filter_params, suffix)

    filter_params = [('Initial Cans', [50, 100]), ('Weights', ['1-Inter'])]
    suffix = '50,100-Intersection'
    create_graph(output_d, param_name, 'Intersection', filter_params, suffix)
    for m_score in scores:
        filter_params = [('Initial Cans', [50, 100]), ('Weights', [f'1-Homo_1-{m_score}'])]
        suffix = f'50,100-{m_score}'
        create_graph(output_d, param_name, m_score, filter_params, suffix)


def create_param_graphs(param_name):
    output_d = f'{output_dir}{param_name}/'
    Functions.create_directory(output_d)
    scores = ['Gender', 'Age', 'BMI']

    filter_params = [('Stopping Criteria', [0.01, 0.05, 0.1]), ('Top Cans', [1, 3, 5, 7, 10]), ('Weights', ['1-Inter'])]
    suffix = 'Intersection'
    create_graph(output_d, param_name, 'Intersection', filter_params, suffix)
    for m_score in scores:
        filter_params = [('Stopping Criteria', [0.01, 0.05, 0.1]), ('Top Cans', [1, 3, 5, 7, 10]), ('Weights', [f'1-Homo_1-{m_score}'])]
        suffix = f'{m_score}'
        create_graph(output_d, param_name, m_score, filter_params, suffix)


def create_weights_graphs():
    param_name = 'Weights'
    output_d = f'{output_dir}{param_name}/'
    Functions.create_directory(output_d)

    scores = ['Gender', 'Age', 'BMI']

    for w1, w2 in itertools.combinations(scores, 2):

        filter_params = [('Stopping Criteria', [0.01, 0.05, 0.1]), ('Top Cans', [1, 3, 5, 7, 10]),
                         ('Weights', [f'1-Homo_1-{w1}'] + [w for w in weights if (w1 in w) and (w2 in w)] + [f'1-Homo_1-{w2}'])]
        suffix = f'{w1}-{w2}'
        create_weights_graph(output_d, param_name, w1, w2, filter_params, suffix)
        create_weights_graph(output_d, param_name, w2, w1, filter_params, suffix)
        # break

def instance_to_graph(intervals, states):
    xs, ys = [], []
    for interval, state in zip(intervals, states):
        xs.append([interval[0], interval[1]])
        ys.append([state] * 2)
    return ys, xs

params_names = ['Initial Cans', 'TIRPs Size']  # 'Weights', 'Initial Cans', 'TIRPs Size', 'Stopping Criteria'
scores_names = ['Coverage', 'Total Score', 'Intersection', 'Gender', 'Age', 'BMI']  # Number of TIRPs
weights = ['1-Homo_1-Gender', '1-Homo_1-Age', '1-Homo_1-BMI',
           '1-Homo_0.67-Gender_0.33-Age', '1-Homo_0.67-Gender_0.33-BMI',
           '1-Homo_0.33-Gender_0.67-Age', '1-Homo_0.67-Age_0.33-BMI',
           '1-Homo_0.33-Gender_0.67-BMI', '1-Homo_0.33-Age_0.67-BMI']

for dataset_name in Glob.Datasets_Names:
    output_dir = f'{Glob.Graphs_Dir_Path}{dataset_name}/'
    Functions.create_directory(output_dir)
    dp = DataParser(f'{Glob.Results_Dir_Path}{dataset_name}')
    dp.parse_files()
    # create_weights_graphs()
    # create_param_graphs_split_by_initial_cans('Stopping Criteria')
    # for param in params_names:
    #     create_param_graphs(param)
    dp.results_df.to_csv('results.csv')

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







