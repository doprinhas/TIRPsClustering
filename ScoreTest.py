import numpy as np


def dis_log_sigma(vals, b=2):
    score = 0
    for val in vals:
        score += (val*np.log(val, b))
    return score