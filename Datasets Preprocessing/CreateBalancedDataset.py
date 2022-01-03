import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import Globals as Glob


def get_entities_properties(dir_path):
    ent_props = {}
    for file in os.listdir(dir_path):
        if '_Demo.json' in file:
            prop = file[:-10]
            ent_props[prop] = json.load(open(f'{dir_path}{file}'))
            values = list(ent_props[prop].values())
            # print(min(values), max(list(ent_props[prop].values())))
            plt.clf()
            plt.hist(values, bins='auto')
            plt.show()
    return ent_props
    #     {
    #     'BMI': json.load(open(f'{MetaData_Dir_Path}entities bmi.json')),
    #     'Age': json.load(open(f'{MetaData_Dir_Path}entities ages.json')),
    #     'Gender': json.load(open(f'{MetaData_Dir_Path}entities genders.json'))
    # }


def create_entities_index_matrix():
    global rel_ids
    indexes_matrix = initial_index_matrix()
    for id in rel_ids:
        bins = get_entity_bins_indexes(id)
        indexes_matrix[bins].add(id)
    return indexes_matrix


def initial_index_matrix():
    global props_cutoffs
    size = [len(prop_bins)+1 for prop_bins in props_cutoffs.values()]
    return np.frompyfunc(set, 0, 1)(np.empty(size, dtype=object))


def get_entity_bins_indexes(id):
    global entities_props, props_cutoffs
    bins_indexes = []
    for prop, p_cutoffs in props_cutoffs.items():
        bins_indexes.append(get_value_bin(p_cutoffs, entities_props[prop][id]))
    return tuple(bins_indexes)


def get_value_bin(cutoffs, val):
    for i, cutoff in enumerate(cutoffs):
        if val <= cutoff:
            return i
    return len(cutoffs)


def is_dataset_balanced(delta=5):
    global bins_counter
    for prop, prop_counter in bins_counter.items():
        for bin_i in range(len(prop_counter)):
            for bin_j in range(bin_i, len(prop_counter)):
                bins_diff = np.abs(prop_counter[bin_i] - prop_counter[bin_j])
                if bins_diff > delta:
                    return False
    return True


def add_to_counter(bins):
    global bins_counter
    for bin, prop in zip(bins, bins_counter):
        bins_counter[prop][bin] += 1


def remove_from_counter(bins):
    global bins_counter
    for bin, prop in zip(bins, bins_counter):
        bins_counter[prop][bin] -= 1


def add_entity(fun=np.argmin):
    global entities_index_matrix, chosen_index_matrix, rel_ids, dataset_entities
    bins = get_bins(fun)
    if len(entities_index_matrix[bins]) == 0:
        return False
    ent = entities_index_matrix[bins].pop()
    chosen_index_matrix[bins].add(ent)
    rel_ids.remove(ent)
    dataset_entities.add(ent)
    add_to_counter(bins)
    return ent


def remove_entity(fun=np.argmax):
    global entities_index_matrix, chosen_index_matrix, rel_ids, dataset_entities
    bins = get_bins(fun)
    if len(chosen_index_matrix[bins]) == 0:
        return False
    ent = chosen_index_matrix[bins].pop()
    entities_index_matrix[bins].add(ent)
    dataset_entities.remove(ent)
    rel_ids.add(ent)
    remove_from_counter(bins)
    return ent


def random_index(l):
    return np.random.randint(0, len(l))


def get_bins(fun):
    global bins_counter
    bins = []
    for prop_counter in bins_counter.values():
        bins.append(fun(prop_counter))
    return tuple(bins)

dataset_name = 'icu'
dir_path = f'{Glob.MetaData_Dir_Path}{dataset_name}/'
rel_ids = set(json.load(open(f'{dir_path}ids.json')))  # change to get the entities ids
print(len(rel_ids))
dataset_size = 400
delta = 1
props_cutoffs = {"Gender": [0.5], "Age": [60, 65, 70, 75]}

entities_props = get_entities_properties(dir_path)  # change to get the entities properties
dataset_entities = set()
entities_index_matrix = create_entities_index_matrix()
chosen_index_matrix = initial_index_matrix()
bins_counter = {
    prop: [0] * (len(props_cutoffs[prop])+1)
    for prop in props_cutoffs
}

while (len(dataset_entities) < dataset_size) or (not is_dataset_balanced(delta)):
    if len(dataset_entities) == dataset_size:
        remove_entity()
    else:

        if not add_entity():
            if is_dataset_balanced(delta):
                add_entity(random_index)
                # print(len(dataset_entities), bins_counter)
            else:
                remove_entity()
                print(len(dataset_entities), bins_counter)


print(len(dataset_entities))
print(bins_counter)

file = open(f'{dir_path}{dataset_size}_B_ids.json', 'w')
json.dump(list(dataset_entities), file)
file.close()
file = open(f'{dir_path}{dataset_size}_B_Cutoffs.json', 'w')
json.dump(props_cutoffs, file)
file.close()


# import json
# file = open(f'homogeneity scores.json')
# tirps_homogeneity_scores = json.load(file)
# file.close()
# scores = list(tirps_homogeneity_scores.values())
# scores.sort(key=lambda x: x[0], reverse=True)