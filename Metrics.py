import numpy as np
import Globals as Glob


tirps_intersection = {}


def solution_scores(solution):
    cov = coverage(solution.tirps)[0]
    int = intersection(solution.tirps)[0]
    # homo = solution_homogeneity(solution)
    return cov, int, solution.score


def picking_score(tirp, tirps, weights):
    scores, score_elements = {}, {}
    # if weights['C'] > 0:
    scores['C'], score_elements['C'] = coverage([tirp])
    if weights['I'] > 0:
        scores['I'], score_elements['I'] = picking_intersection(tirp, tirps)
    if weights['H'] > 0:
        scores['H'], score_elements['H'] = homogeneity(tirp, weights['HW'])
    return calculate_score(scores, weights), score_elements


def calculate_score(scores, weights):
    total_score = 0
    if weights['I'] > 0:
        total_score -= (weights['I'] * scores['I'])
    if weights['H'] > 0:
        total_score += weights['H'] * scores['H']
    return total_score


def coverage(tirps):
    sets = [tirp.entities for tirp in tirps]
    s = set().union(*sets)
    return len(s) / tirps[0].population_size(), s


def intersection(tirps):
    # TODO: change implementation that uses the dictionary
    inter = 0
    for i, tirp1 in enumerate(tirps):
        for tirp2 in tirps[i+1:]:
            inter += tirp1.proportional_intersection(tirp2)
    avg_inter = inter/((len(tirps) * (len(tirps)-1))/2)
    return avg_inter, avg_inter


def picking_intersection(tirp, tirps):
    # TODO: change implementation that uses the dictionary ?
    inter = 0
    for c_tirp in tirps:
        inter += (len(tirp.intersection(c_tirp))/tirp.population_size())
    avg_inter = inter/len(tirps)
    return avg_inter, 0


def homogeneity(tirp, weights):
    scores = Glob.homogeneity_scores[tirp.file_name]
    h_score = 0
    for var in scores:
        h_score += scores[var] * weights[var]
    return h_score, h_score


def solution_homogeneity(solution):
    vars = Glob.Tirps_Scores[solution.tirps[0].file_name]
    scores = {}
    for var in vars:
        scores[var] = np.mean([Glob.homogeneity_scores[tirp.file_name][var] for tirp in solution.tirps])
    return scores


def continues_coverage(tirp, prev_set):
    s = prev_set.union(tirp.entities)
    return len(s) / tirp.population_size(), s


def continues_intersection(tirp, tirps, prev):
    global tirps_intersection
    cur_avg_inter = 0
    for tirp_i in tirps:
        if (tirp.description, tirp_i.description) in tirps_intersection:
            cur_avg_inter += (tirps_intersection[(tirp.description, tirp_i.description)])
        else:
            cur_avg_inter += (tirps_intersection[(tirp_i.description, tirp.description)])
    cur_avg_inter = cur_avg_inter/len(tirps)
    total_num_of_pairs = (len(tirps) * (len(tirps)+1))/2
    avg_inter = (len(tirps)/total_num_of_pairs)*cur_avg_inter + ((total_num_of_pairs-len(tirps))/total_num_of_pairs)*prev
    return avg_inter, avg_inter


def continues_homogeneity(tirp, weights, len_tirps, prev):
    h_score = homogeneity(tirp, weights)[0] + (prev * (len_tirps-1))
    h_score = h_score / len_tirps
    return h_score, h_score


def continues_avg_score(tirp, len_tirps, prev):
    h_score = tirp.score + (prev * (len_tirps-1))
    h_score = h_score / len_tirps
    return h_score, h_score