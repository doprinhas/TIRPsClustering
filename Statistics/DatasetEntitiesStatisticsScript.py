import os
import json
import numpy as np
import Globals as Glob
from Graphs import StatisticsGraphs as Graphs
import HelpFunctions as Functions

def get_entities_ids(dir_path):
    lines = open(f'{dir_path}KL.txt').readlines()[2:]
    ids = []
    for i in range(0, len(lines), 2):
        ent_id = lines[i].split(';')[0]
        ids.append(ent_id)
    return ids


def get_at_bins_count(ids, homogeneity, at_cutoffs):
    counts = [0] * (len(at_cutoffs)+1)
    vals = []
    for id in ids:
        bin_i = get_bin_index(homogeneity[id], at_cutoffs)
        counts[bin_i] += 1
        vals.append(homogeneity[id])
    return counts, vals


def get_bin_index(val, cutoffs):
    for bin_index, cutoff in zip(range(len(cutoffs)), cutoffs):
        if val < cutoff:
            return bin_index
    return len(cutoffs)


def cutoffs_to_strings(cutoffs, at_var):
    if at_var == 'Gender':
        return ['Males', 'Females']
    str_cutoffs = [f'{at_var} < {cutoffs[0]}']
    for prev_c, next_c in zip(cutoffs[:-1], cutoffs[1:]):
        str_cutoffs.append(f'{prev_c} <= {at_var} < {next_c}')
    str_cutoffs.append(f'{cutoffs[-1]} <= {at_var}')
    return str_cutoffs


for dataset in Glob.Datasets_Names:

    metadata_dir_path = f'{Glob.MetaData_Dir_Path}{Functions.get_metadata_dir_name(dataset)}/'
    dir_path = f'{Glob.KL_O_Dir_Path}{dataset}/'
    homogeneity = json.load(open(f'{dir_path}entities characteristics.json'))  # TODO: Change
    ids = get_entities_ids(dir_path)
    props_cutoffs = Functions.get_props_cutoffs(metadata_dir_path)

    for at_var in homogeneity:
        bins_count, vals = get_at_bins_count(ids, homogeneity[at_var], props_cutoffs[at_var])
        x_labels = cutoffs_to_strings(props_cutoffs[at_var], at_var)
        path = f'{Glob.Statistics_Graphs_Dir_Path}{dataset}/'
        Functions.create_directory(path)
        Graphs.create_at_groups(f'{path}{at_var} dis.png', x_labels, bins_count, at_var)
        print(f'{at_var}: {round(np.mean(vals), 2)} ({round(np.std(vals), 2)})')


