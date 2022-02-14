import pandas as pd
import numpy as np
import time as t
import Globals as Glob
import HelpFunctions as Functions
import itertools as itt
import ScoreFunctions as sf
import CreateKLFile, CreateStatesFile

import matplotlib.pyplot as plt
import HelpFunctions as Functions

EntityID = 'EntityID'
TimeStamp = 'TimeStamp'
TemporalPropertyID = 'TemporalPropertyID'
TemporalPropertyValue = 'TemporalPropertyValue'


def parse_input_files(path):
    df = pd.read_csv(path)
    st = t.time_ns()
    entities_groups = parse_entities_groups(df.query(f'{TemporalPropertyID} == -1'))
    print(f'parse_entities_groups - Time: {glob.get_time_passed(st, u="sec")} sec')
    st = t.time_ns()
    groups_values, entities_values = parse_values_to_groups(df.query(f'{TemporalPropertyID} != -1'), entities_groups)
    print(f'parse_values_to_groups - Time: {glob.get_time_passed(st, u="sec")} sec')
    return groups_values, entities_values, entities_groups


def parse_entities_groups(props_cutoffs, entities_char_props, ids):
    entities_groups = {}
    for ent_id in ids:
        entities_groups[ent_id] = {}
        for prop in entities_char_props:
            entities_groups[ent_id][prop] = Functions.get_value_bin(props_cutoffs[prop], entities_char_props[prop][ent_id])
    return entities_groups


def get_variables_values_per_entity(csv_file_path, ids):
    vars = set()#df[TemporalPropertyID].unique()
    entities_values = {
        ent_id: {
            str(var): [] for var in vars
        }
        for ent_id in ids
    }
    entities_timestamps = {
        ent_id: {
            str(var): [] for var in vars
        }
        for ent_id in ids
    }
    lines = open(csv_file_path).readlines()
    for line in lines[1:]:
        s_line = line[:-1].split(',')
        ent_id, var, ts, val = s_line
        if var not in vars:
            vars.add(var)
        if var not in entities_values[ent_id]:
            entities_values[ent_id][var] = []
            entities_timestamps[ent_id][var] = []
        entities_values[ent_id][var].append(float(val))
        entities_timestamps[ent_id][var].append(int(ts))

    return entities_values, entities_timestamps, vars


def get_variables_values_per_prop_group(entities_values, entities_props_groups, variables, props_cutoffs):
    groups_values = initialize_groups_values_dict(variables, entities_props_groups, props_cutoffs)
    for var in variables:
        for ent_id, ent_vals in entities_values.items():
            for prop, group_i in entities_props_groups[ent_id].items():
                if var in ent_vals:
                    groups_values[var][prop][group_i].extend(ent_vals[var])
    return groups_values


def initialize_groups_values_dict(variables, entities_props_groups, props_cutoffs):
    props = list(entities_props_groups[list(entities_props_groups.keys())[0]].keys())
    groups_values = {
        var: {
            prop: [] for prop in props
        }
        for var in variables
    }
    for var in variables:
        for prop in props:
            cutoffs = props_cutoffs[prop]
            for i in range(len(cutoffs)+1):
                groups_values[var][prop].append([])
    return groups_values


def parse_values_to_groups(values_df,):
    groups = set(entities_groups.values())
    ids = values_df[EntityID].unique()
    groups_values = {var: {gr: [] for gr in groups} for var in values_df[TemporalPropertyID]}
    entities_values = {id: {} for id in ids}
    for prop in values_df[TemporalPropertyID].unique():
        prop_df = values_df.query(f'{TemporalPropertyID} == {prop}')
        for id in ids:
            ent_prop_df = prop_df.query(f'{EntityID} == {id}')
            vals = list(ent_prop_df[TemporalPropertyValue])
            ts = list(ent_prop_df[TimeStamp])
            groups_values[prop][entities_groups[id]].extend(vals)
            entities_values[id][prop] = (ts, vals)
    return groups_values, entities_values


def get_cutoffs_options(prop_groups_values, cutoffs_options_function=None, options_num=100):
    if not cutoffs_options_function:
        return sorted(cutoffs_options_all_values(prop_groups_values))
    return sorted(cutoffs_options_function(prop_groups_values, options_num))


def cutoffs_options_all_values(prop_groups_values):
    return set(prop_groups_values)


def cutoffs_options_equal_width_spilt(prop_all_groups_values, options_num=100):
    optional_cutoffs = []
    min_val, max_val = min(prop_all_groups_values), max(prop_all_groups_values)
    gap = (max_val - min_val) / options_num
    for i in range(1, options_num + 1):
        optional_cutoffs.append(gap * i)
    return optional_cutoffs


def cutoffs_options_equal_frequency_spilt(prop_all_groups_values, options_num=100):
    # TODO: rewrite this function
    prop_all_groups_values.sort()
    values_count = get_values_count(prop_all_groups_values)
    sorted_vals = sorted(list(values_count.keys()))

    if len(values_count) <= options_num:
        return sorted_vals[1:]

    optional_cutoffs = []
    vals_sum, val_i = 0, 1
    bin_count = values_count[sorted_vals[0]]

    for option_i in range(options_num):

        if options_num > (len(values_count) - val_i) + len(optional_cutoffs):
            return optional_cutoffs + sorted_vals[options_num-len(optional_cutoffs):]
        val_per_bin = int((len(prop_all_groups_values) - vals_sum) / (options_num + 1 - option_i))

        while val_i < len(sorted_vals)-1 and \
                abs(val_per_bin - (bin_count + values_count[sorted_vals[val_i]])) < abs(val_per_bin - bin_count):
            bin_count += values_count[sorted_vals[val_i]]
            val_i += 1

        optional_cutoffs.append(sorted_vals[val_i])
        vals_sum += bin_count
        bin_count = values_count[sorted_vals[val_i]]
        val_i += 1

    return optional_cutoffs


def cutoffs_options_equal_values_frequency_spilt(prop_all_groups_values, options_num=100):
    prop_all_groups_values = list(set(prop_all_groups_values))
    return cutoffs_options_equal_frequency_spilt(prop_all_groups_values, options_num)


def get_values_count(values):
    values_count = {}
    for val in values:
        if val in values_count:
            values_count[val] += 1
        else:
            values_count[val] = 1
    return values_count


def get_all_groups_values(prop_groups_values):
    all_vals = []
    for gr_vals in prop_groups_values.values():
        for vals in gr_vals:
            all_vals.extend(vals)
    return all_vals


def find_best_cutoffs(groups_values, bins_entities_count, cutoffs_options, num_of_cutoffs, method):
    combinations = itt.combinations(cutoffs_options, num_of_cutoffs)
    groups_values_count = []
    for gr_vals in groups_values:
        groups_values_count.append(get_values_count(gr_vals))
    max_score = float('-inf')
    # best_cutoffs = []
    for comb in combinations:
        bins_vs = calc_bins_vs(comb, bins_entities_count)
        score, rel_counters = calc_homogeneity_score(comb, groups_values_count, bins_vs, method)
        # score = sf.get_score(groups_values, list(comb), score_fun)
        if score > max_score:
            max_score = score
            best_cutoffs = list(comb), rel_counters
    return best_cutoffs


def calc_bins_vs(cutoffs, bins_entities_count):
    # st = t.time_ns()
    bins_vs = [list() for i in range(len(cutoffs)+1)]
    for val, ent_set in bins_entities_count.items():
        bin_i = get_value_bin(cutoffs, val)
        bins_vs[bin_i].append(ent_set)
    bins_vs = [set().union(*vals) for vals in bins_vs]
    bins_vs = np.array([len(s) for s in bins_vs])
    bins_vs = bins_vs/population_size
    # print(f'Time {Functions.get_time_passed(st, r=10)} sec')
    return bins_vs


def calc_homogeneity_score(cutoffs, groups_values_count, bins_vs, method='Conditional Mean Homo + Max Bins Variance'):
    scores = []
    counters = bins_counters(cutoffs, groups_values_count)
    rel_counters = []
    prop_base_score = np.log2(1 / (len(cutoffs)+1))

    for bin, bin_dis in counters.items():
        hom_score, rel_bins_count = calc_sigma_log(bin_dis)
        hom_score = (prop_base_score - hom_score) / prop_base_score
        bin_rel_size = np.sum(bin_dis) / len(all_values)
        # score = np.mean([hom_score, bins_vs[bin], bin_rel_size])
        score = hom_score * bins_vs[bin]
        scores.append(score) # 0 if max_bin in max_bins else
        rel_counters.append(rel_bins_count)
        # max_bins.add(max_bin)
    return np.mean(scores), counters


def global_homogeneity(counters, prop_base_score):
    counters_mean = np.mean(counters, axis=0)
    hom_score, rel_bins_count = calc_sigma_log(counters_mean)
    return (prop_base_score - hom_score) / prop_base_score


def calc_sigma_log(values):
    bins_count = np.array(values)
    rel_bins_count = bins_count / np.sum(values)
    return np.nansum(rel_bins_count*np.log2(rel_bins_count)), rel_bins_count


def count_bins(cutoffs, values):
    counters = [0] * (len(cutoffs)+1)
    for val, count in values.items():
        bin_num = get_value_bin(cutoffs, val)
        counters[bin_num] += count
    return counters


def bins_counters(cutoffs, values):
    counters = {b: np.zeros(len(values)) for b in range(len(cutoffs)+1)}
    for gr_i in range(len(values)):
        for val, count in values[gr_i].items():
            bin_num = get_value_bin(cutoffs, val)
            counters[bin_num][gr_i] += count
    # for bin, bin_count in counters.items():
    #     counters[bin] = bin_count/np.sum(bin_count)
    return counters


def get_value_bin(cutoffs, val):
    for i, cutoff in enumerate(cutoffs):
        if val <= cutoff:
            return i
    return len(cutoffs)


def get_entities_distinct_values(entities_values):
    return {
        var: {
            _id: set(entities_values[_id][var]) for _id in ids if var in entities_values[_id]
        } for var in variables
    }


def get_bins_entities_count(entities_values, cutoffs_options):
    map_dic = {i: co for i, co in enumerate(cutoffs_options + [float('inf')])}
    bins_entities_set = {co: set() for co in cutoffs_options + [float('inf')]}
    for ent_id, ent_vals in entities_values.items():
        for val in ent_vals:
            bin = get_value_bin(cutoffs_options, val)
            bins_entities_set[map_dic[bin]].add(ent_id)
    return bins_entities_set


def plot_cutoff_vars_distribution(path, dis, labels=['Males', 'Females'],  title=''):
    plt.clf()
    plt.figure(figsize=(8, 10))
    width = (1/len(dis))-0.1
    x_labels = np.arange(len(dis[0]))
    # labels = ['Males', 'Females']
    for i, label in zip(range(len(dis)), labels):
        plt.bar(x_labels+(width*i), dis[i], width, label=label)

    delta = (np.mean(x_labels)/2)*width
    plt.xticks(x_labels+delta, x_labels, fontweight='bold', fontsize=12)
    plt.yticks(fontweight='bold', fontsize=10)

    plt.xlabel('Bins', fontweight='bold', fontsize=12)
    plt.ylabel('Percentage', fontweight='bold', fontsize=12)
    plt.title(title, fontweight='bold', fontsize=16)

    plt.legend()
    # plt.show()
    plt.savefig(path)
# def get_max_bin(bins_counter):
#     max_bin = 0
#     for bin, count in bins_counter.items():
#         if count
#         bins.append(fun(prop_counter))
#     return tuple(bins)

dataset_name = 'deb'
prop = 'Gender'
cutoffs_num = 2
methods = [
           # 'Conditional Mean Homo + Max Bins STD Sum',
           # 'Conditional Mean Homo + Bins Variance Sum',
           'Conditional Mean Homo + Max Bins Variance Sum',
            # 'Conditional Mean Homo + Max Bins Variance Sum - Global Homo',
           # 'Conditional Mean Homo + Max Bins Variance Mean',
           # 'Mean Locals Homo - Global Homo'
]

dataset_dir_path = f'{Glob.KL_O_Dir_Path}{dataset_name}/'
metadata_dir_path = f'{Glob.MetaData_Dir_Path}{Functions.get_metadata_dir_name(dataset_name)}/'

props_cutoffs = Functions.get_props_cutoffs(metadata_dir_path)
entities_char_props = Functions.get_entities_properties(metadata_dir_path, prop)
ids = Functions.get_entities_ids(metadata_dir_path)

st = t.time_ns()
entities_props_groups = parse_entities_groups(props_cutoffs, entities_char_props, ids)
entities_values, entities_timestamps, variables = get_variables_values_per_entity(f'{Glob.HG_I_Dir_Path}{dataset_name}.csv', ids)
props_groups_values = get_variables_values_per_prop_group(entities_values, entities_props_groups, variables,
                                                          props_cutoffs)
entities_values = get_entities_distinct_values(entities_values)
population_size = len(ids)
print(f'Parse Data - Time: {Functions.get_time_passed(st, u="sec")} sec')
for method in methods:
    vars_cutoffs = {}
    for var in sorted(props_groups_values):
        st = t.time_ns()
        # num_of_cutoffs = len(props_groups_values[2]) - 1a
        all_values = get_all_groups_values(props_groups_values[var])
        cutoffs_options = get_cutoffs_options(all_values, cutoffs_options_equal_frequency_spilt, 100)
        bins_entities_count = get_bins_entities_count(entities_values[var], cutoffs_options)
        # print(sf.get_bins_percentage(all_vals, cutoffs_options))

        mt = t.time_ns()
        res = find_best_cutoffs(props_groups_values[var][prop], bins_entities_count, cutoffs_options, cutoffs_num, method)
        # print(var, res)

        co, dis = res
        vars_cutoffs[var] = co
        # path = f'/sise/home/dorpi/Data/ClusDis/{dataset_name}_{prop}_{cutoffs_num}_{method}/'
        # Functions.create_directory(path)
        # plot_cutoff_vars_distribution(f'{path}{var}', dis, ['Men', 'Women'], f'Method: {method}\nVariable: {var}')
        print(f'Cutoffs: {co} -- Dis: {dis} -- Var: {var} -- Time: {Functions.get_time_passed(st, u="sec")} sec')



#
# #
# temporalPropIDs = CreateKLFile.create_temporal_properties_ids_dictionary(vars_cutoffs)
# file_lines = ['startToncepts', f'numberOfEntities,{len(entities_values)}']
# st = t.time_ns()
# for id in ids:
#     file_lines.append(f'{id};')
#     file_lines.append(CreateKLFile.entity_intervals_str(entities_values[id], entities_timestamps[id], vars_cutoffs, temporalPropIDs))
# print(f'KL Lines Creation Time: {Functions.get_time_passed(st, u="sec")} sec')
#
# # output_dir = f'{Glob.HG_O_Dir_Path}{dataset_name}_ClusDis_{}'
# file = open(f'{output_dir}KL.txt', 'w')
# for line in file_lines:
#     file.write(f'{line}\n')
# file.close()
#
# states_df = CreateStatesFile.create_states_df(vars_cutoffs, temporalPropIDs)
# states_df.to_csv(f'{output_dir}states.csv')
