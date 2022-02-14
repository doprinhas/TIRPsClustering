import Metrics


class Solution:

    def __init__(self, tirps, score, score_elements=None):
        self.tirps = tirps
        self.score = score

        if len(tirps) == 1:
            self.score_elements = {
                'C': tirps[0].entities,
                'S': score
            }
            self.coverage = len(tirps[0].entities) / self.tirps[0].population_size()
        elif score_elements:
            self.score_elements = score_elements
            self.coverage = len(self.score_elements['C']) / self.tirps[0].population_size() if score_elements else 0

    def append(self, tirp, new_score, score_elements=None):
        self.tirps.append(tirp)
        self.score = new_score
        self.score_elements = score_elements
        self.coverage = len(self.score_elements['C']) / self.tirps[0].population_size() if score_elements else 0

    def __len__(self):
        return len(self.tirps)

    def get_first(self):
        return self.tirps[0]

    def set_time(self, time):
        self.time = time

    def set_scores(self, scores):
        self.scores = scores

    def mean_homogeneity_score(self):
        score = 0
        for tirp in self.tirps:
            score += tirp.mean_homogeneity
        return score / len(self.tirps)

    def mean_extrapolation_score(self):
        score = 0
        for tirp in self.tirps:
            score += tirp.mean_extrapolation
        return score / len(self.tirps)

    def strict_extrapolation_score(self):
        score = 0
        for tirp in self.tirps:
            score += tirp.strict_extrapolation
        return score / len(self.tirps)

    def continues_score(self, tirp):
        if not self.score_elements:
            return None
        scores, score_elements = {}, {}
        coverage, score_elements['C'] = Metrics.continues_coverage(tirp, self.score_elements['C'])
        score, score_elements['S'] = Metrics.continues_avg_score(tirp, len(self.tirps) + 1,
                                                                 self.score_elements['S'])
        return coverage, score, score_elements
# class Solution:
#
#     def __init__(self, tirps, score, weights, score_elements=None):
#         self.tirps = tirps
#         self.score = score
#         self.score_elements = score_elements
#         self.weights = weights
#         self.coverage = len(self.score_elements['C']) / self.tirps[0].population_size() if score_elements else 0
#
#     def append(self, tirp, new_score, score_elements=None):
#         self.tirps.append(tirp)
#         self.score = new_score
#         self.score_elements = score_elements
#         self.coverage = len(self.score_elements['C']) / self.tirps[0].population_size() if score_elements else 0
#
#     def __len__(self):
#         return len(self.tirps)
#
#     def set_scores(self, scores):
#         self.scores = scores
#
#     def continues_score(self, tirp):
#         if not self.score_elements:
#             return None
#         scores, score_elements = {}, {}
#         scores['C'], score_elements['C'] = Metrics.continues_coverage(tirp, self.score_elements['C'])
#         if self.weights['I'] > 0:
#             scores['I'], score_elements['I'] = Metrics.continues_intersection(tirp, self.tirps, self.score_elements['I'])
#         if self.weights['H'] > 0:
#             scores['H'], score_elements['H'] = Metrics.continues_homogeneity(tirp, self.weights['HW'],
#                                                                              len(self.tirps)+1,
#                                                                              self.score_elements['H'])
#         return scores['C'], Metrics.calculate_score(scores, self.weights), score_elements
