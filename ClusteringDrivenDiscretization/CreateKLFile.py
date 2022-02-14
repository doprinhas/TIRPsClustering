

def entity_intervals_str(entity_data, entity_timestamps, cutoffs, temporalPropIDs):

    intervals = []

    for var in entity_data:
        intervals.extend(create_entity_var_intervals(var, temporalPropIDs, entity_data[var], entity_timestamps[var], cutoffs[var]))

    intervals.sort()
    return f'{intervals}'[1:-1].replace(' ', '').replace('[', '').replace('],', ';').replace(']', ';')


def create_entity_var_intervals(var, temporalPropIDs, values, timestamps, cutoffs):
    intervals = [[timestamps[0]]]
    bin_index = value_bin(values[0], cutoffs)
    for i in range(len(values)):
        cur_bin = value_bin(values[i], cutoffs)
        if bin_index != cur_bin:
            intervals[-1].extend([timestamps[i], temporalPropIDs[var][bin_index], int(var)])
            intervals.append([timestamps[i]])
            bin_index = cur_bin
    intervals[-1].extend([timestamps[-1], temporalPropIDs[var][bin_index], int(var)])
    return intervals


def value_bin(val, cutoffs):
    for i in range(len(cutoffs)):
        if val < cutoffs[i]:
            return i
    return len(cutoffs)


def create_temporal_properties_ids_dictionary(vars_cutoffs):

    temporal_properties_ids = {var: {} for var in vars_cutoffs}
    temp_prop_id = 1

    for var, cutoffs in vars_cutoffs.items():
        for bin in range(len(cutoffs)+1):
            temporal_properties_ids[var][bin] = temp_prop_id
            temp_prop_id += 1

    return temporal_properties_ids