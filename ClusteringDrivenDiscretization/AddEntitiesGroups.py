import pandas as pd
import numpy as np
import json
import Globals as glob


def get_bin_index(val, cutoffs):
    for index, co in zip(range(len(cutoffs)), cutoffs):
        if val < co:
            return index
        index += 1
    return len(cutoffs)

df_path = 'D:\\Documents\\University\\Lab-KarmaLego\\SleepApnea\\Data\\Matched EDFs_1Sec_All\\750_2-3H_2,5,8.csv'
df = pd.read_csv(df_path, index_col=None)
file = open('../Data/MetaData/entities bmi.json')
bmis = json.loads(file.read())

bmi_cutoffs = [18.5, 25, 30]

ids = list(df['EntityID'].unique())
entities_group = {}

for id in ids:
    entities_group[id] = get_bin_index(bmis[str(id)], bmi_cutoffs)

entities_group_df = {col: [] for col in df.columns[1:]}
for id in ids:
    entities_group_df[glob.EntityID].append(id)
    entities_group_df[glob.TemporalPropertyID].append(-1)
    entities_group_df[glob.TimeStamp].append(0)
    entities_group_df[glob.TemporalPropertyValue].append(entities_group[id])


entities_group_df = pd.DataFrame(entities_group_df)

# TODO: More General Script
# TODO: Remove IDs with Data
