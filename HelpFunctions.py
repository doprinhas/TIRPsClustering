import os
import shutil
import json
import time as t
import numpy as np
import pandas as pd
import pickle as pkl
import itertools as itt
from math import comb
import multiprocessing as mp

import Metrics
from ClusteringTIRP import ClusteringTIRP
from concurrent.futures import ThreadPoolExecutor


def get_thread_pool_executor(max_workers):
    return ThreadPoolExecutor(max_workers=max_workers)


def get_process_pool_executor(max_workers):
    return mp.Pool(processes=max_workers)


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def copy_file(src, des):
    shutil.copy2(src, des)


def save_solution_tirps(solution, dataset_path, output_dir):
    for c in solution.tirps:
        file = open(f'{output_dir}{c.file_name}'.replace('.tirp', '.pkl'), 'wb')  # saves tirp pickle obj
        pkl.dump(c, file)
        file.close()
        copy_file(f'{dataset_path}{c.file_name}', f'{output_dir}{c.file_name}')  # copy tirp file to results folder
    copy_file(f'{dataset_path}states.csv', f'{output_dir}states.csv')  # copy states file from KL Output to results


# def write_results(results, output_path):
#     # TODO Change
#     df = {'Scores': ['Number of Clusters', 'Total Score', 'Coverage', 'Intersection']}
#     for top_cans in results:
#         scores = list(Metrics.solution_scores(results[top_cans]))
#         df[top_cans] = [len(results[top_cans])] + [results[top_cans].score] + scores[:-1] + list(scores[-1].values())
#         df[top_cans].append([tirp.file_name for tirp in results[top_cans].tirps])
#     # df = {top_cans: [results[top_cans].score] for top_cans in results}
#     df['Scores'].extend(list(scores[-1].keys()))
#     df['Scores'].append('TIRPs')
#     df = pd.DataFrame(df)
#     df.to_csv(output_path, index=False)

def write_results(results, output_path):
    # TODO: Change
    df = {'Scores': ['Number of Clusters', 'Total Score', 'Coverage', 'Intersection']}
    for top_cans in results:
        scores = list(Metrics.solution_scores(results[top_cans]))
        df[top_cans] = [len(results[top_cans]), results[top_cans].score, results[top_cans].coverage, scores[1]]
        df[top_cans].append([tirp.file_name for tirp in results[top_cans].tirps])

    # df['Scores'].extend(list(scores[-1].keys()))
    df['Scores'].append('TIRPs')
    df = pd.DataFrame(df)
    df.to_csv(output_path, index=False)



def get_population_size(dir_path):
    line = open(f'{dir_path}KL.txt').readlines()[1]
    return int(line.split(',')[1])


def create_entities_index_dic(dir_path):
    lines = open(f'{dir_path}KL.txt').readlines()[2:]
    dic, ent_index = {}, 0
    for i in range(0, len(lines), 2):
        ent_id = int(lines[i].split(';')[0])
        dic[ent_id] = ent_index
        ent_index += 1
    return dic


def dataset_max_tirp_size(dataset_path):
    for root, dirs, files in os.walk(dataset_path):
        files.sort(reverse=True)
        for file in files:
            if '.tirp' in file:
                break
        k = get_tirp_size(file)
        return k


def get_tirps(dir_path, tirps_size, ent_index_dic=None):
    tirps = []
    for file in os.listdir(dir_path):
        if '.tirp' in file and get_tirp_size(file) == tirps_size:
            tirps.append(ClusteringTIRP(f'{dir_path}{file}', ent_index_dic))
    return tirps


def get_tirps_files_names(dir_path, tirps_size):
    tirps = []
    for file in os.listdir(dir_path):
        if '.tirp' in file and get_tirp_size(file) == tirps_size:
            tirps.append(file)
    return tirps


def get_tirp_size(tirp_name):
    return int(tirp_name.split(' ')[0])


def save_coverage(path, tirps):
    file = open(path, 'w')
    cov, ent = Metrics.coverage(tirps)
    file.write(f'{cov}\n{ent}')
    file.close()
    return cov


def get_time_passed(start_time, u="min", r=2):
    time_sec = (t.time_ns() - start_time) / 10**9
    if u == "sec":
        return round(time_sec, r)
    elif u == "min":
        return round(time_sec / 60, r)
    elif u == "h":
        return round(time_sec / 3600, r)


def weights_to_dir_name(weights):
    # dir_name = f'_{weights["C"]}-Cov' if weights['C'] > 0 else ''
    dir_name = f'_{weights["I"]}-Inter' if weights['I'] > 0 else ''
    if weights['H'] > 0:
        dir_name += f'_{weights["H"]}-Homo'
        for var in weights['HW']:
            dir_name += f'_{round(weights["HW"][var], 2)}-{var}' if weights["HW"][var] > 0 else ''
    return dir_name[1:]


def create_candidates_intersection_dictionary(candidates):
    inter_dic = {}
    for i in range(len(candidates)):
        for j in range(i+1, len(candidates)):
            tirp_1, tirp_2 = candidates[i], candidates[j]
            inter_dic[(tirp_1.description, tirp_2.description)] = tirp_1.proportional_intersection(tirp_2)
    Metrics.tirps_intersection = inter_dic


def get_entities_properties(dir_path):
    demo_dict = {}
    for file in os.listdir(dir_path):
        if '_Demo.json' not in file:
            continue
        prop = file.split('_')[0]
        demo_dict[prop] = json.load(open(f'{dir_path}{file}'))
    return demo_dict


def get_metadata_dir_name(dataset_name):
    name = dataset_name.split('_')[0]
    try:
        int(name)
        return 'SAHS'
    except:
        return name


def get_props_cutoffs(dir_path):
    for file in os.listdir(dir_path):
        if '_Cutoffs.json' not in file:
            continue
        return json.load(open(f'{dir_path}{file}'))