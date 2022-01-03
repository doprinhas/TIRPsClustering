import time as t
import HelpFunctions as Functions
import Metrics
import Log
from Solution import Solution
from ClusteringTIRP import ClusteringTIRP
import Globals as Glob


# def pick_candidates(tirps, weights, max_workers=8):
#
#     # executor = Functions.get_thread_pool_executor(max_workers)
#     executor = Functions.get_process_pool_executor(max_workers)
#     tirps_scores = []
#
#     for tirp in tirps:
#         # executor.submit(add_tirp_score, tirps_scores, tirp, tirps, weights)
#
#         # tirps_scores.append(
#         #     executor.submit(add_tirp_score, tirp, tirps, weights)
#         #                     )
#         tirps_scores.append(
#             executor.apply_async(add_tirp_score, (tirp, tirps, weights))
#         )
#         # tirp_score, score_elements = Metrics.picking_score(tirp, tirps, weights)
#         # sol_can = Solution([tirp], tirp_score, weights, score_elements)
#         # tirps_scores.append(sol_can)
#
#     # executor.shutdown(wait=True)
#     executor.close()
#     # tirps_scores = [sol.result() for sol in tirps_scores]
#     tirps_scores = [sol.get() for sol in tirps_scores]
#
#     tirps_scores.sort(reverse=True, key=lambda can: can.score)
#     return tirps_scores


# def add_tirp_score(tirp, tirps, weights):
#     tirp_score, score_elements = Metrics.picking_score(tirp, tirps, weights)
#     return Solution([tirp], tirp_score, weights, score_elements)


def pick_candidates(tirps_names, scores):

    tirps_scores = [(tirp_name, scores[tirp_name]) for tirp_name in tirps_names]
    tirps_scores.sort(reverse=True, key=lambda t: t[1])
    tirps_scores = tirps_scores[:max(Glob.Initial_Cans_Op)]

    ent_index_dic = Functions.create_entities_index_dic(Glob.Dataset_Path)
    candidates = []
    for tirp_name, tirp_score in tirps_scores:
        tirp = ClusteringTIRP(f'{Glob.Dataset_Path}{tirp_name}', scores[tirp_name], ent_index_dic)
        candidates.append(Solution([tirp], tirp_score))

    candidates.sort(reverse=True, key=lambda s: s.score)
    return candidates


def expand_top_cans(chosen, candidates, top_cans, eps, path):
    top_chosen = get_top_chosen(chosen, candidates, eps)

    solutions, index = [], 0
    for chosen_can in top_chosen[:top_cans if top_cans != 'Optimal' else len(top_chosen)]:
        index += 1
        candidates.remove(chosen_can.tirps[-1])
        solutions.append(expand_top_cans(chosen_can, set(candidates), top_cans, eps, path + [index]))

    solutions.sort(reverse=True, key=lambda sol: sol.score)
    return solutions[0] if len(solutions) > 0 else chosen


def get_top_chosen(chosen, candidates, eps):
    if chosen.coverage == Glob.Possible_Coverage:
        return []
    top_candidates = []
    for can in candidates:
        cov, score, score_elements = chosen.continues_score(can)
        if (len(chosen) < 2) or ((chosen.coverage + eps) < cov):
            tirps = chosen.tirps + [can]
            top_candidates.append((Solution(tirps, score, score_elements)))
    top_candidates.sort(reverse=True, key=lambda c: c.score)
    return top_candidates