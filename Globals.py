import os

Dataset_Name = 'SAHS_300_B_3-4_sax_3_1_30_7_10_True'
Tirp_Size = 0
Initial_Cans_Op = [100]
Top_Cans_Op = [1, 5, 10]
Epsilons_Op = [0]

homogeneity_scores = None
Tirps_Scores = None

Possible_Coverage = 0
KL_O_Dir_Path = "/sise/robertmo-group/Dor/Data/KL Output/"  #  '../Data/KL Output/'  #
HG_I_Dir_Path = "/sise/robertmo-group/Dor/Data/Hugobot Input/"
HG_O_Dir_Path = "/sise/robertmo-group/Dor/Data/Hugobot Output/"
Datasets_Dir_Path = "/sise/robertmo-group/Dor/Data/Datasets/"
Clusters_Results_Dir_Path = '/home/dorpi/Data/Clusters/'
MetaData_Dir_Path = '/sise/robertmo-group/Dor/Data/MetaData/'
Graphs_Dir_Path = '/home/dorpi/Data/Graphs/'
Statistics_Graphs_Dir_Path = '/home/dorpi/Data/Graphs/Statistics/'

Dataset_Path = f'{KL_O_Dir_Path}{Dataset_Name}/'
Results_Dir_Path = f'{Clusters_Results_Dir_Path}{Dataset_Name}_Abstraction_Exp/'
# Datasets_Names = [d for d in os.listdir(Clusters_Results_Dir_Path) if '3_1' in d]
# Datasets_Names = [d for d in os.listdir(Clusters_Results_Dir_Path) if '_B' in d and 'MM_' in d]
Datasets_Names = \
    ['icu_sax_3_1_20_7_30_True', 'deb_sax_3_1_10_7_60_True']#[d for d in os.listdir(KL_O_Dir_Path) if '_B' not in d and 'sax_3_1_30_7_10_True' in d][-2:-1]

Min_Tirps_Size = 6
Prioritize_Metrics_Weights = [
    # Gender
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 1,
            'Age': 0,
            'BMI': 0
        }
    }
]

rev_props_ids_dic = {
    1: 'Snore',
    2: 'Flow',
    3: 'Thorax',
    4: 'Abdomen',
    5: 'SpO2',
    6: 'Pleth',
    7: 'Pulse',
    8: 'Activity',
    9: 'Position',
    10: 'Sum Effort',
    '1': 'Snore',
    '2': 'Flow',
    '3': 'Thorax',
    '4': 'Abdomen',
    '5': 'SpO2',
    '6': 'Pleth',
    '7': 'Pulse',
    '8': 'Activity',
    '9': 'Position',
    '10': 'Sum Effort'
}

