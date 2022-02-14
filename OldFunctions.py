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


def weights_to_ticks(ws):
    ticks = []
    for w in ws:
        ticks.append(w[7:].replace('_', '\n'))
    return ticks


def switch(l, i, j):
    l[i], l[j] = l[j], l[i]


def switch_ys(ys, i, j):
    for y in ys:
        switch(y, i, j)


def create_weights_graph(output_dir, param_name, main_score, sec_score, filter_params, suffix=''):
    x, ys, labels = dp.get_results_by_param_topcans_split(param_name, main_score, filter_params)
    x = weights_to_ticks(x)
    sort_weights(main_score, sec_score, x, ys)
    file_name, title = \
        f'{output_dir}{main_score}-{param_name}', f'Average Solution\'s {main_score} as a function of {param_name}'
    if suffix != '':
        file_name.replace('.png', f' -- {suffix}.png'); title += f' -- {suffix}'

    Graphs.plot_multi_line_chart(file_name, x, ys, labels, title
                                 , param_name, main_score)


def create_param_graphs_split_by_initial_cans(param_name):
    output_d = f'{output_dir}{param_name}/'
    Functions.create_directory(output_d)

    filter_params = [('Initial Cans', [30])]
    # create_graph(output_d, param_name, 'Intersection', filter_params, '30')
    create_graph(output_d, param_name, 'Total Score', filter_params, f'30')

    filter_params = [('Initial Cans', [50, 100])]
    # create_graph(output_d, param_name, 'Intersection', filter_params, '50,100-Intersection')
    create_graph(output_d, param_name, 'Total Score', filter_params, f'50,100')