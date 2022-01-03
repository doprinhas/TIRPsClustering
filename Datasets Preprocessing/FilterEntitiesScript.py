import pandas as pd
import json
import Globals as Glob

dataset_name = 'ahe'
size = 2000

ids = [int(id) for id in json.load(open(f'{Glob.MetaData_Dir_Path}{dataset_name}/{size}_B_ids.json'))]
df = pd.read_csv(f'{Glob.Datasets_Dir_Path}{dataset_name}/{dataset_name}.csv')

print(df['EntityID'].nunique())
df = df.query(f'EntityID in {ids}')
print(df['EntityID'].nunique(), len(ids))

df.to_csv(f'{Glob.HG_I_Dir_Path}{dataset_name}_{size}_B.csv')