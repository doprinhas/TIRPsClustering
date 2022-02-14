import pandas as pd
import numpy as np
import os


class DataParser:

    def __init__(self, path):
        self.exp_path = path
        self.results = {
            'TIRPs Size': [],
            # 'Weights': [],
            'Initial Cans': [],
            'Stopping Criteria': [],
            'Top Cans': [],
            'Number of Clusters': [],
            'Mining Coverage': [],
            'Initial Candidates Coverage': [],
            'Coverage': [],
            'Score': [],
            'Intersection': [],
            'Mean Homogeneity': [],
            'Mean Extrapolation': [],
            'Strict Extrapolation': [],
            # 'Old Score': [],
            # 'Gender': [],
            # 'Age': [],
            # 'BMI': [],
            'TIRPs': [],
            'Time': []
        }
        self.top_cans = []

    def parse_files(self):
        path = self.exp_path
        for tirp_size in [int(d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
            mining_cov = self.read_coverage(f'{self.exp_path}/{tirp_size}/MiningCoverage.txt')
            self.read_initial_cans_dirs(f'{self.exp_path}/{tirp_size}', tirp_size, mining_cov)
        self.results_df = pd.DataFrame(self.results)

    def read_weights_comb_dirs(self, path, tirp_size, mining_cov=0):
        for weight_comb in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
            self.read_initial_cans_dirs(f'{path}/{weight_comb}', tirp_size, weight_comb, mining_cov)

    def read_initial_cans_dirs(self, path, tirp_size, mining_cov=0):
        for initial_cans in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
            self.read_results_files(f'{path}/{initial_cans}', tirp_size, initial_cans, mining_cov)

    def read_results_files(self, path, tirp_size, initial_cans, mining_cov=0):
        for file in [f for f in os.listdir(path)]:
            if '.csv' in file and 'states' not in file:
                picking_cov = self.read_coverage(f'{path}/InitialCansCoverage.txt')
                self.insert_to_results(path, file, tirp_size,
                                       initial_cans, float(file[:-4]), picking_cov, mining_cov)

    def insert_to_results(self, dir_path, file_name, tirp_size, initial_cans, epsilon, picking_cov, mining_cov=0):
        dic = self.parse_df(pd.read_csv(f'{dir_path}/{file_name}'))
        self.top_cans = list(dic['Number of Clusters'].keys())
        self.scores = list(dic.keys())
        for top_cans in self.top_cans:
            self.results['TIRPs Size'].append(int(tirp_size))
            # self.results['Weights'].append(weights_comb)
            self.results['Initial Cans'].append(int(initial_cans))
            self.results['Stopping Criteria'].append(float(epsilon))
            self.results['Top Cans'].append(top_cans)
            self.results['Initial Candidates Coverage'].append(picking_cov)
            self.results['Mining Coverage'].append(mining_cov)

            for score in self.scores:
                if score == 'TIRPs':
                    self.results[score].append([f'{dir_path}/{tirp_name}' for tirp_name in dic[score][top_cans]])
                else:
                    try:
                        self.results[score].append(dic[score][top_cans])
                    except:
                        self.results[f'Mean {score}'].append(dic[score][top_cans])

    def parse_df(self, df):
        results = {}
        for index, row in df.iterrows():
            results[row['Scores']] = {}
            for top_cans in df.columns[1:]:
                try:
                    val = float(row[top_cans])
                except:
                    val = row[top_cans][2:-2].split("', '")
                try:
                    top_cans = int(top_cans)
                except:
                    top_cans = top_cans

                results[row['Scores']][top_cans] = val

        return results

    def read_coverage(self, path):
        return float(open(path).readlines()[0][:-1])

    def get_unique(self, col):
        return sorted(list(self.results_df[col].unique()))

    def get_results_by_param_topcans_split(self, param_name, score, filter_prams=[], z=1.96):
        df = self.results_df
        for f_param in filter_prams:
            df = df.query(f'`{f_param[0]}` in {f_param[1]}')
        ys = []
        errors = []
        x = list(df[param_name].unique())
        try:
            x = [float(v) for v in x]
        except:
            pass
        x.sort()
        labels = list(df['Top Cans'].unique())
        labels.sort()
        for top_cans in labels:
            if top_cans == 'Optimal':
                y = df.query(f'`Top Cans`=="{top_cans}"').groupby(param_name).mean()
                err = df.query(f'`Top Cans`=="{top_cans}"').groupby(param_name).std()
                count = df.query(f'`Top Cans`=="{top_cans}"').groupby(param_name).count()
            else:
                y = df.query(f'`Top Cans`=={top_cans}').groupby(param_name).mean()
                err = df.query(f'`Top Cans`=={top_cans}').groupby(param_name).std()
                count = df.query(f'`Top Cans`=={top_cans}').groupby(param_name).count()
            y = y.sort_values(param_name)
            err = err.sort_values(param_name)
            count = count.sort_values(param_name)
            try:
                ci = list(err[score]*z / np.sqrt(count[score]))
                ys.append(list(y[score]) + [None] * (len(x) - len(y)))
            except:
                score = f'Mean {score}'
                ci = list(err[score]*z / np.sqrt(count[score]))
                ys.append(list(y[score]) + [None] * (len(x) - len(y)))
            errors.append(ci + [None] * (len(x) - len(y)))

        if score == 'Coverage':
            y = df.groupby(param_name).mean()
            y = y.sort_values(param_name)
            err = df.groupby(param_name).std()
            err = err.sort_values(param_name)
            count = df.groupby(param_name).count()
            count = count.sort_values(param_name)
            ys.append(list(y['Initial Candidates Coverage']))
            ci = err['Initial Candidates Coverage']*z / np.sqrt(count['Initial Candidates Coverage'])
            errors.append(list(ci))
            labels.append('Initial Candidates Coverage')
            ys.append(list(y['Mining Coverage']))
            ci = err['Mining Coverage']*z / np.sqrt(count['Mining Coverage'])
            errors.append(list(ci))
            labels.append('Mining Coverage')
        return x, ys, errors, labels

    def get_results_by_param_initcans_split(self, param_name, score, filter_prams=[], z=1.96):
        df = self.results_df
        for f_param in filter_prams:
            df = df.query(f'`{f_param[0]}` in {f_param[1]}')
        ys = []
        errors = []
        x = list(df[param_name].unique())
        try:
            x = [float(v) for v in x]
        except:
            pass
        x.sort()
        labels_col = 'Initial Cans'
        labels = list(df[labels_col].unique())
        labels.sort()
        for label in labels:

            y = df.query(f'`{labels_col}`=={label}').groupby(param_name).mean()
            err = df.query(f'`{labels_col}`=={label}').groupby(param_name).std()
            count = df.query(f'`{labels_col}`=={label}').groupby(param_name).count()
            y = y.sort_values(param_name)
            err = err.sort_values(param_name)
            count = count.sort_values(param_name)
            try:
                ci = list(err[score]*z / np.sqrt(count[score]))
                ys.append(list(y[score]) + [None] * (len(x) - len(y)))
            except:
                score = f'Mean {score}'
                ci = list(err[score]*z / np.sqrt(count[score]))
                ys.append(list(y[score]) + [None] * (len(x) - len(y)))
            errors.append(list(ci) + [None] * (len(x) - len(y)))

        if score == 'Coverage':
            y = df.groupby(param_name).mean()
            y = y.sort_values(param_name)
            err = df.groupby(param_name).std()
            err = err.sort_values(param_name)
            count = df.groupby(param_name).count()
            count = count.sort_values(param_name)
            ys.append(list(y['Initial Candidates Coverage']))
            ci = err['Initial Candidates Coverage']*z / np.sqrt(count['Initial Candidates Coverage'])
            errors.append(list(ci))
            labels.append('Initial Candidates Coverage')
            ys.append(list(y['Mining Coverage']))
            ci = err['Mining Coverage']*z / np.sqrt(count['Mining Coverage'])
            errors.append(list(ci))
            labels.append('Mining Coverage')
        return x, ys, errors, labels


def ci(x):
    print(x)
    return np.percentile(x[param_name], [2.5])[0]
