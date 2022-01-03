import Metrics as pm

homogeneity_scores = None
Tirps_Scores = None

Possible_Coverage = 0
KL_O_Dir_Path = "/sise/robertmo-group/Dor/Data/KL Output/"  #  '../Data/KL Output/'  #
HG_I_Dir_Path = "/sise/robertmo-group/Dor/Data/Hugobot Input/"
Datasets_Dir_Path = "/sise/robertmo-group/Dor/Data/Datasets/"
Results_Dir_Path = '../Data/Clusters/'
MetaData_Dir_Path = '/sise/robertmo-group/Dor/Data/MetaData/'
Graphs_Dir_Path = '../Data/Graphs/'
Statistics_Graphs_Dir_Path = '../Data/Graphs/Statistics/'

Dataset_Name = 'deb_1700_B_sax_7_1_15_7_30_True'
Dataset_Path = f'{KL_O_Dir_Path}{Dataset_Name}/'
Results_Dir_Path = f'{Results_Dir_Path}{Dataset_Name}/'
Datasets_Names = [
    '300_B_3-4_sax_7_1_15_7_20_True',
    '300_B_3-4_sax_7_1_15_7_30_True',
    'ahe_2000_B_sax_7_1_15_7_30_True',
    'deb_1700_B_sax_7_1_10_7_60_True',
    'deb_1700_B_sax_7_1_15_7_30_True',
    'icu_400_B_sax_7_1_15_7_30_True'
    # 'deb_1700_B_sax_7_1_15_7_30_True',
    # 'icu_400_B_sax_7_1_15_7_30_True'
    # '300_B_3-4_sax_7_1_15_7_30_True'
    # 'deb_1700_B_sax_7_1_15_7_30_True'
    # 'SleepApnea'
    # '1300_3H_2,5,7,8,9_sax_3_0_20_7_10_True',
    # 'DIABETES_sax_3_0_20_7_10_True',
    # 'HEPATITIS_sax_3_0_20_7_10_True',
    # 'icu_sax_3_0_20_7_10_True'
]
Min_Tirps_Size = 6
Tirp_Size = 4
Initial_Cans_Op = [20]
Top_Cans_Op = [1, 3, 5, 7, 10, 'Optimal']
Epsilons_Op = [0, 0.01, 0.05, 0.1]
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
    },
    # Age
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 0,
            'Age': 1,
            'BMI': 0
        }
    },
    # BMI
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 0,
            'Age': 0,
            'BMI': 1
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 2/3,
            'Age': 1/3,
            'BMI': 0
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 2/3,
            'Age': 0,
            'BMI': 1/3
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 1/3,
            'Age': 2/3,
            'BMI': 0
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 0,
            'Age': 2/3,
            'BMI': 1/3
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 1/3,
            'Age': 0,
            'BMI': 2/3
        }
    },
    {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 0,
            'Age': 1/3,
            'BMI': 2/3
        }
    },     {
        'I': 0,
        'H': 1,
        'HW': {
            'Gender': 1/3,
            'Age': 1/3,
            'BMI': 1/3
        }
    },
    # Intersection
    # {
    #     'I': 1,
    #     'H': 0,
    #     'HW': {}
    # }
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