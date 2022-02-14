import pandas as pd


def create_states_df(vars_cutoffs, temporal_props_ids):
    dic = {
        'StateID': [],
        'TemporalPropertyID': [],
        'BinID': [],
        'BinLow': [],
        'BinHigh': [],
        'Method': [],
    }

    for var in vars_cutoffs:
        cutoffs_bounds = [float('-inf')] + vars_cutoffs[var] + [float('inf')]
        for bin_id, state_id, bin_low, bin_high in \
                zip(range(len(temporal_props_ids[var])), temporal_props_ids[var], cutoffs_bounds[:-1], cutoffs_bounds[1:]):
            dic['StateID'].append(temporal_props_ids[var][state_id])
            dic['TemporalPropertyID'].append(var)
            dic['BinID'].append(bin_id)
            dic['BinLow'].append(bin_low)
            dic['BinHigh'].append(bin_high)
            dic['Method'].append('ClusteringDriven')

    return pd.DataFrame(dic)