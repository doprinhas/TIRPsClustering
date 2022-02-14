import pandas as pd
import numpy as np
import scipy.stats


def confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    se = scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h


dirs = ['500_2-3H_2,5,8_clustering-driven-BMI_4_0_10_3_10_True',
        '500_2-3H_2,5,8_clustering-driven-BMI_4_0_10_3_10_True-1',
        '500_2-3H_2,5,8_equal-frequency_4_5_10_3_10_True',
        '500_2-3H_2,5,8_kmeans_4_5_10_3_10_True',
        '500_2-3H_2,5,8_sax_4_5_10_3_10_True',
        '500_2-3H_2,5,8_equal-width_4_5_10_3_10_True']

for i in range(2, 6):
    print(f'K: {i}')
    for dir in dirs:
        try:
            df = pd.read_csv(f'../Data/Graphs/{dir}/{i} BMIs.csv')
            print(f'{dir.split("_")[3]} Error Mean: {np.mean(df["error"])} Error CI: {confidence_interval(df["error"])}'
                  f'Min: {df["error"][0]}')
        except:
            pass

