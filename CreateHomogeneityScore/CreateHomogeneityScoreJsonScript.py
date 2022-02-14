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
        props_base_score[prop] = np.log2(1 / (1+len(props_cutoffs[prop])))
        # values = [entities_char_prop[prop][str(ent_id)] for ent_id in ids]
        # cb = count_bins(props_cutoffs[prop], values)
        # props_base_score[prop] = calc_sigma_log(list(cb.values()))

    return props_base_score

def get_props_bins_count():
    global ids, entities_char_prop, props_cutoffs
    props_bins_count = {}
    for prop in entities_char_prop:
        values = [entities_char_prop[prop][str(ent_id)] for ent_id in ids]
        props_bins_count[prop] = count_bins(props_cutoffs[prop], values)

    return props_bins_count

def calc_extrapolation(tirp):
    global props_bins_count
    ids = [str(id) for id in tirp.entities]
    bins_count = create_entities_bins_count(ids)
    max_bins = get_bins(bins_count)
    props_extra = {}
    for (prop, bins_counts), max_bin in zip(bins_count.items(), max_bins):
        props_extra[prop] = bins_counts[max_bin] / props_bins_count[prop][max_bin]
    return props_extra

def calc_strict_extrapolation(tirp):
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
    global ids
    try:
        tirp = ClusteringTIRP(path, pop_size=len(ids))
        homo = calc_tirp_homogeneity_score(tirp)
        mean_homo = np.mean(list(homo.values()))
        st_extra = calc_strict_extrapolation(tirp)
        extra = calc_extrapolation(tirp)
        mean_extra = np.mean(list(extra.values()))
        return tirp.file_name, homo, extra, mean_homo, mean_extra, st_extra, tirp.coverage(), multiply_combined_score(mean_homo, mean_extra)
    except:
        os.remove(path)
        name = path.split('/')[-1]
        print(name)
        return name, -1, {}, -1, -1, -1, -1, -1


def average_combined_score(homo, extra, hw=0.5):
    return hw * homo + (1-hw) * extra


def multiply_combined_score(homo, extra):
    return homo * extra


def get_weighted_average_score(tirps_scores, hw=0.5):
    mean_min_max_scores = {}
    for tirp, tirp_scores in tirps_scores.items():
        mean_min_max_scores[tirp] = average_combined_score(tirp_scores[0], tirp_scores[1], hw=hw)

    return mean_min_max_scores


def get_mean_min_max_scores(tirps_scores, com_fun=average_combined_score):
    homo_list = [s[0] for s in tirps_scores.values()]
    extra_list = [s[1] for s in tirps_scores.values()]
    min_homo, min_extra = min(homo_list), min(extra_list)
    delta_homo, delta_extra = max(homo_list)-min_homo, max(extra_list)-min_extra

    mean_min_max_scores = {}
    for tirp, tirp_scores in tirps_scores.items():
        mm_homo = (tirp_scores[0] - min_homo) / delta_homo
        mm_extra = (tirp_scores[1] - min_extra) / delta_extra
        mean_min_max_scores[tirp] = com_fun(mm_homo, mm_extra)

    return mean_min_max_scores


results = {}
# [d for d in os.listdir(Glob.KL_O_Dir_Path) if 'deb' in d and '_10_7_60_True' in d]
# [d for d in os.listdir(Glob.KL_O_Dir_Path) if 'icu' in d and '_20_7_30_True' in d]
for dataset_name in ['SAHS_300_3-4_sax_3_1_30_7_10_True']:
    # dataset_name += '_10_7_60_True'
    print(f'Start - {dataset_name}')

    dataset_dir_path = f'{Glob.KL_O_Dir_Path}{dataset_name}/'
    metadata_dir_path = f'{Glob.MetaData_Dir_Path}{Functions.get_metadata_dir_name(dataset_name)}/'

    # props_cutoffs = {"Gender": [0.5], "Age": [40, 52, 64], "BMI": [25, 30]}
    props_cutoffs = Functions.get_props_cutoffs(metadata_dir_path)
    entities_char_prop = Functions.get_entities_properties(metadata_dir_path, 'Gender')

    props_bins_counter = {prop: [0]*(len(props_cutoffs[prop])+1) for prop in entities_char_prop}
    tirps_scores = {}
    tirps_homo_extra_components = {}
    tirps_homo_extra = {}
    tirps_vs = {}
    file = open(f'{dataset_dir_path}/entities characteristics.json', 'w')
    file.write(json.dumps(entities_char_prop))
    file.close()
    ids = Functions.create_entities_index_dic(dataset_dir_path)

    props_hom_base_score = get_props_hom_base_score()
    props_bins_count = get_props_bins_count()
    entities_index_matrix = create_entities_index_matrix([str(id) for id in ids])
    # props_distribution(props_bins_counter, list(ids.keys()))
    executor = Functions.get_thread_pool_executor(30)
    files = os.listdir(dataset_dir_path)
    st = t.time_ns()
    futures = []
    for i, file in enumerate(files):
        if '.tirp' in file:
            futures.append(
                executor.submit(tirp_score, f'{dataset_dir_path}{file}')
            )

        if (i+1) % (int(len(files)/20)) == 0:

            for f in futures:
                name, homo, extra, mean_homo, mean_extra, st_extra, vs, old_score = f.result()
                # tirps_scores[name] = mean_homo, mean_extra
                tirps_homo_extra_components[name] = homo, extra
                tirps_homo_extra[name] = [mean_homo, mean_extra, st_extra, old_score]
                tirps_vs[name] = vs
            futures = []
            perc = (i+1) / len(files)
            left = len(files) - i
            passed_time = ((t.time_ns() - st) / 10**9)
            avg_time = passed_time / i
            print(f'percentage finished: {round(perc*100, 1)}%, Time Passed: {round(passed_time/60, 2)} min, ETA: {round((avg_time * left)/60, 2)} min')

    for f in futures:
        name, homo, extra, mean_homo, mean_extra, st_extra, vs, old_score = f.result()
        # tirps_scores[name] = mean_homo, mean_extra
        tirps_homo_extra_components[name] = homo, extra
        tirps_homo_extra[name] = [mean_homo, mean_extra, st_extra, old_score]
        tirps_vs[name] = vs
    executor.shutdown(wait=True)

    # tirps_min_max_scores = get_weighted_average_score(tirps_homo_extra, hw=0.9)
    tirps_min_max_scores = get_mean_min_max_scores(tirps_homo_extra)
    # scores = list(tirps_min_max_scores.values())
    # scores.sort(reverse=True)
    scores = []
    for tirp, score in tirps_homo_extra.items():
        scores.append((score[0], score[1], tirps_vs[tirp], tirp))
    scores.sort(reverse=True)
    # print(entities_char_prop.keys(), scores[0])
    results[dataset_name] = scores[:10]

    file = open(f'{dataset_dir_path}scores.json', 'w')
    file.write(json.dumps(tirps_min_max_scores))
    file.close()
    file = open(f'{dataset_dir_path}homo&extraComp.json', 'w')
    file.write(json.dumps(tirps_homo_extra_components))
    file.close()
    file = open(f'{dataset_dir_path}homo&extra.json', 'w')
    file.write(json.dumps(tirps_homo_extra))
    file.close()
    file = open(f'{dataset_dir_path}VS.json', 'w')
    file.write(json.dumps(tirps_vs))
    file.close()
    print(f'File Size: {round(os.path.getsize(f"{dataset_dir_path}/scores.json")/2**20, 2)} MB')
    print(f'Time: {round((t.time_ns() - st) / (60*10**9), 2)} min')


for d, ss in results.items():
    print(d)
    for s in ss:
        print(s)