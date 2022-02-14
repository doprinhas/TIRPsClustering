import pandas as pd
import json
import Globals as Glob


def create_dict_from_df(df, val_col, key_col='EntityID'):
    d = {}
    for i, row in df.iterrows():
        if row[key_col] in ids:
            d[row[key_col]] = row[val_col]
    return d



datasets = ['deb']
demo_vars = ['Married']
for dataset_name in datasets:

    dir_path = f'{Glob.Datasets_Dir_Path}{dataset_name}/'
    path = f'{dir_path}{dataset_name}_demographic.csv'
    demographic_variables_df = pd.read_csv(path)
    df = pd.read_csv(f'{Glob.Datasets_Dir_Path}{dataset_name}/{dataset_name}.csv')
    ids = list(df['EntityID'].unique())
    print(min(demographic_variables_df['age']), max(demographic_variables_df['age']))

    for var in demo_vars:
        d = create_dict_from_df(demographic_variables_df, var)
        file = open(f'{Glob.MetaData_Dir_Path}{dataset_name}/{var}_Demo.json', 'w')
        json.dump(d, file)
        file.close()

    dir_path = f'{Glob.MetaData_Dir_Path}{dataset_name}/'
    path = f'{dir_path}Age_Demo.json'
    d = json.load(open(path))


    file = open(f'{Glob.MetaData_Dir_Path}{dataset_name}/ids.json', 'w')
    json.dump(list(d.keys()), file)
    file.close()
    print(len(d))



# demographic_variables_df['gender'] = demographic_variables_df['gender'].apply(lambda x: 0 if x == 'M' else 1)
# demographic_variables_df.to_csv(path)
