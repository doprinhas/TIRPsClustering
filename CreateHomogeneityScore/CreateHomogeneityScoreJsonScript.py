import json
import os
import time as t
import numpy as np
import pandas as pd

import Globals as Glob
from ClusteringTIRP import ClusteringTIRP
import HelpFunctions as Functions
np.seterr(divide='ignore', invalid='ignore')


def calc_tirp_homogeneity_score(tirp):
    # TODO: Implement with ThreadPool?
    global entities_char_prop, props_hom_base_score, props_cutoffs
    tirp_scores = {}
    try:
        for prop in entities_char_prop:
            values = [entities_char_prop[prop][str(ent_id)] for ent_id in tirp.entities]
            tirp_scores[prop] = calc_score(props_cutoffs[prop], values, props_hom_base_score[prop])
    except:
        print(tirp.file_name)
    return tirp_scores


def calc_score(cutoffs, values, prop_base_score):
    counters = count_bins(cutoffs, values)
    hom_score = calc_sigma_log(list(counters.values()))
    hom_score = (hom_score - prop_base_score) / prop_base_score
    hom_score = np.abs(hom_score)
    return hom_score


def count_bins(cutoffs, values):
    counters = {i: 0 for i in range(len(cutoffs)+1)}
    for val in values:
        bin_num = get_value_bin(cutoffs, val)
        counters[bin_num] += 1
    return counters


def get_value_bin(cutoffs, val):
    for i, cutoff in enumerate(cutoffs):
        if val <= cutoff:
            return i
    return len(cutoffs)


def props_distribution(props_bins_counter, ids):
    global entities_char_prop, props_cutoffs
    for id in ids:
        for prop in entities_char_prop:
            bin_num = get_value_bin(props_cutoffs[prop], entities_char_prop[prop][str(id)])
            props_bins_counter[prop][bin_num] += 1


def calc_sigma_log(values):
    bins_count = np.array(values)
    rel_bins_count = bins_count / np.sum(values)
    return np.nansum(rel_bins_count*np.log2(rel_bins_count))


def get_props_hom_base_score():
    global ids, entities_char_prop, props_cutoffs
    props_base_score = {}
    for prop in entities_char_prop:
        values = [entities_char_prop[prop][str(ent_id)] for ent_id in ids]
        cb = count_bins(props_cutoffs[prop], values)
        props_base_score[prop] = calc_sigma_log(list(cb.values()))

    return props_base_score


def calc_extrapolation(tirp):
    global entities_index_matrix
    ids = [str(id) for id in tirp.entities]
    index_matrix = create_entities_index_matrix(ids)
    bins_count = create_entities_bins_count(ids)
    max_bins = get_bins(bins_count)
    return len(index_matrix[max_bins]) / len(entities_index_matrix[max_bins]) if len(entities_index_matrix[max_bins]) > 0 else 0\
       # , len(index_matrix[max_bins]), len(entities_index_matrix[max_bins]), len(ids)


def create_entities_index_matrix(ids):
    indexes_matrix = initial_index_matrix()
    for id in ids:
        bins = get_entity_bins_indexes(id)
        indexes_matrix[bins].add(id)
    return indexes_matrix


def create_entities_bins_count(ids):
    bins_counter = initial_bins_counter()
    for id in ids:
        bins = get_entity_bins_indexes(id)
        add_to_counter(bins_counter, bins)
    return bins_counter


def add_to_counter(bins_counter, bins):
    for bin, prop in zip(bins, bins_counter):
        bins_counter[prop][bin] += 1


def initial_bins_counter():
    global entities_char_prop, props_cutoffs
    return {
        prop: [0] * (len(props_cutoffs[prop])+1)
        for prop in entities_char_prop
    }


def initial_index_matrix():
    global entities_char_prop, props_cutoffs
    size = [len(props_cutoffs[prop])+1 for prop in entities_char_prop]
    return np.frompyfunc(set, 0, 1)(np.empty(size, dtype=object))


def get_entity_bins_indexes(id):
    global entities_char_prop, props_cutoffs
    bins_indexes = []
    for prop in entities_char_prop:
        bins_indexes.append(get_value_bin(props_cutoffs[prop], entities_char_prop[prop][id]))
    return tuple(bins_indexes)


def get_bins(bins_counter, fun=np.argmax):
    bins = []
    for prop_counter in bins_counter.values():
        bins.append(fun(prop_counter))
    return tuple(bins)


def tirp_score(path):
    tirp = ClusteringTIRP(path)
    mean_homo = np.mean(list(calc_tirp_homogeneity_score(tirp).values()))
    extra = calc_extrapolation(tirp)
    return tirp.file_name, mean_homo * extra



for dataset_name in Glob.Datasets_Names:
    print(f'Start - {dataset_name}')

    dataset_dir_path = f'{Glob.KL_O_Dir_Path}{dataset_name}/'
    metadata_dir_path = f'{Glob.MetaData_Dir_Path}{Functions.get_metadata_dir_name(dataset_name)}/'

    # props_cutoffs = {"Gender": [0.5], "Age": [40, 52, 64], "BMI": [25, 30]}
    props_cutoffs = Functions.get_props_cutoffs(metadata_dir_path)
    entities_char_prop = Functions.get_entities_properties(metadata_dir_path)

    props_bins_counter = {prop: [0]*(len(props_cutoffs[prop])+1) for prop in entities_char_prop}
    tirps_scores = {}
    file = open(f'{dataset_dir_path}/entities characteristics.json', 'w')
    file.write(json.dumps(entities_char_prop))
    file.close()
    ids = Functions.create_entities_index_dic(dataset_dir_path)

    props_hom_base_score = get_props_hom_base_score()
    entities_index_matrix = create_entities_index_matrix([str(id) for id in ids])
    # props_distribution(props_bins_counter, list(ids.keys()))
    executor = Functions.get_thread_pool_executor(15)
    files = os.listdir(dataset_dir_path)
    st = t.time_ns()
    futures = []
    for i, file in enumerate(files):
        if '.tirp' in file:
            futures.append(
                executor.submit(tirp_score, f'{dataset_dir_path}{file}')
            )
            # tirp = ClusteringTIRP(f'{dataset_dir_path}{file}')
            # mean_homo = np.mean(list(calc_tirp_homogeneity_score(tirp).values()))
            # extra = calc_extrapolation(tirp)
            # tirps_scores[file] = mean_homo * extra

        if (i+1) % (int(len(files)/100)) == 0:

            for f in futures:
                name, score = f.result()
                tirps_scores[name] = score
            futures = []
            perc = (i+1) / len(files)
            left = len(files) - i
            avg_time = ((t.time_ns() - st) / 10**9) / i
            print(f'percentage finished: {round(perc*100, 1)}%, ETA: {round((avg_time * left)/60, 2)} min')

    for f in futures:
        name, score = f.result()
        tirps_scores[name] = score
    executor.shutdown(wait=True)
    file = open(f'{dataset_dir_path}scores.json', 'w')
    file.write(json.dumps(tirps_scores))
    file.close()
    print(f'File Size: {round(os.path.getsize(f"{dataset_dir_path}/scores.json")/2**20, 2)} MB')
    print(f'Time: {round((t.time_ns() - st) / (60*10**9), 2)} min')


scores = list(tirps_scores.values())
scores.sort(reverse=True)
print(scores[0])