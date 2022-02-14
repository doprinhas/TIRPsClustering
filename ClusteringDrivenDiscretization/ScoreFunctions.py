import numpy as np


def i_bin_proportionate_share_score(group_i_values, cutoffs, i):
    counter = 0
    cutoffs = [float('-inf')] + cutoffs + [float('inf')]
    for val in group_i_values:
        if cutoffs[i] <= val < cutoffs[i+1]:
            counter += 1
    return counter / len(group_i_values)


def sum_percentage_differences_from_i_bin_score(group_i_values, cutoffs, i):
    bins_perc = get_bins_percentage(group_i_values, cutoffs)
    i_bin_perc = bins_perc.pop(i)
    score = 0

    for bin_p in bins_perc:
        score += (i_bin_perc - bin_p)

    return score


def i_bin_percentage_difference_from_other_buns(group_i_values, cutoffs, i):
    i_bin_perc = i_bin_proportionate_share_score(group_i_values, cutoffs, i)
    return 2*i_bin_perc - 1


def i_bin_difference_from_other_bins_mean(group_i_values, cutoffs, i):
    bins_perc = get_bins_percentage(group_i_values, cutoffs)
    i_bin_perc = bins_perc.pop(i)
    return i_bin_perc - np.mean(bins_perc)


def get_bins_percentage(group_i_values, cutoffs):
    bins_count = [0]
    values_sort = list(group_i_values)
    values_sort.sort()
    i_cutoff = 0
    cur_sum = 0

    for index, val in zip(range(len(values_sort)), values_sort):
        if i_cutoff == len(cutoffs):
            break
        if val >= cutoffs[i_cutoff]:
            bins_count.append(index - cur_sum)
            cur_sum += bins_count[-1]
            i_cutoff += 1
    bins_count.append(len(group_i_values) - cur_sum)
    # fill zeros at the end
    bin_prec = [val / len(group_i_values) for val in bins_count[1:]] + [0] * (len(cutoffs)-len(bins_count)+2)
    return bin_prec


def get_score(var_groups_values, cutoffs, score_fun):
    score = 0
    for index, var_group in zip(range(len(var_groups_values)), var_groups_values):
        score += score_fun(var_groups_values[var_group], cutoffs, index)
    return score


score_functions = {
    'proportionate_share_score': i_bin_proportionate_share_score,
    # 'sum_percentage_differences_from_i_bin_score': sum_percentage_differences_from_i_bin_score,
    # 'percentage_difference_from_other_buns': i_bin_percentage_difference_from_other_buns,
    # 'difference_from_other_bins_mean': i_bin_difference_from_other_bins_mean
}
