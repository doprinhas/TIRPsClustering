import subprocess
import time
import os


def change_globals_parameters(params):
    with open('/home/dorpi/TIRPsClustering/Globals.py') as file:
        lines = file.readlines()
    for i, p_line in zip(range(2, 9), params):
        lines[i] = p_line
    with open('/home/dorpi/TIRPsClustering/Globals.py', 'w') as file:
        file.writelines(lines)


def validate_changes(params):
    with open('/home/dorpi/TIRPsClustering/Globals.py') as file:
        lines = file.readlines()
    for i, p_line in zip(range(2, 9), params):
        if lines[i] != p_line:
            return False
    return True


def dataset_max_tirp_size(dataset_path):
    files = os.listdir(dataset_path)
    files.sort(reverse=True)
    for file in files:
        if '.tirp' in file:
            break
    k = get_tirp_size(file)
    return k


def get_tirp_size(tirp_name):
    return int(tirp_name.split(' ')[0])


def create_data_set_params_options(dataset_name, initial_cans_op=[100], epsilons=[0.01]):
    dataset_path = f'{KL_O_Dir_Path}{dataset_name}/'
    max_tirp_size = dataset_max_tirp_size(dataset_path)
    params_options = []
    # for in_cans in initial_cans_op:
    #     for tirp_size in range(2, max_tirp_size + 1):
    #         for eps in epsilons:
    #             params_options.append(get_param_option(dataset_name, tirp_size, in_cans, eps))
    for in_cans in initial_cans_op:
        for eps in epsilons:
            params_options.append(get_param_option(dataset_name, 0, in_cans, eps))
    return params_options


def get_param_option(dataset_name, tirp_size, initial_cans, epsilon):
    # if initial_cans <= 30:
    #   return [
    #     f"Dataset_Name = '{dataset_name}'\n",
    #     # f"Dataset_Path = f'{KL_O_Dir_Path}{dataset_name}/'\n",
    #     # f"Results_Dir_Path = f'{Results_Dir_Path}{dataset_name}/'\n",
    #     f"Tirp_Size = {tirp_size}\n",
    #     f"Initial_Cans_Op = [{initial_cans}]\n",
    #     "Top_Cans_Op = [1, 5, 10, 'Optimal']\n",
    #     "Epsilons_Op = [0.01, 0.05, 0.1]\n"
    #   ]
    # else:
    return [
        f"Dataset_Name = '{dataset_name}'\n",
        f"Tirp_Size = {tirp_size}\n",
        f"Initial_Cans_Op = [{initial_cans}]\n",
        "Top_Cans_Op = [10]\n",
        f"Epsilons_Op = [{epsilon}]\n"
    ]


def get_number_of_jobs(user_name):
    result = subprocess.run(['squeue', '--me'], stdout=subprocess.PIPE)
    number_of_jobs = str(result.stdout).count(user_name)
    return number_of_jobs


def run_job_using_sbatch(sbatch_path, job_name):
    # os.system(f'sbatch "{sbatch_path}"')
    run_list = ["sbatch", sbatch_path]  # + ["--job-name", job_name]
    subprocess.Popen(run_list, stdout=temp_file, stderr=temp_file)


temp_file = open("tmp.txt", 'w')

user_name = 'dorpi'
sbatch_path = "/home/dorpi/TIRPsClustering/sbatch/sbatch_experiment_run.example"
KL_O_Dir_Path = "/sise/robertmo-group/Dor/Data/KL Output/"
Results_Dir_Path = '/home/dorpi/Data/Clusters/'

# Datasets_Names = [d for d in os.listdir(KL_O_Dir_Path) if 'sax_3_1_30_7_10' in d and 'B' in d]
# Datasets_Names = [d for d in os.listdir(KL_O_Dir_Path) if '_B' in d and 'sax_3_1_30_7_10_True' in d]# ['SAHS_300_B_3-4_sax_3_1_30_7_10_True', 'icu_400_B_sax_3_1_30_7_10_True']
#   [
#   # 'ahe_2000_B_sax_7_1_15_7_30_True',
#   '300_B_3-4_sax_7_1_15_7_30_True',
#   # 'deb_1700_B_sax_7_1_10_7_60_True',
#   'deb_1700_B_sax_7_1_15_7_30_True',
#   # 'icu_400_B_sax_7_1_15_7_30_True',
#   'icu_400_B_sax_7_1_15_7_30_True'
# ]
Datasets_Names = [d for d in os.listdir(KL_O_Dir_Path) if 'deb' in d and '_10_7_60_True' in d] + [d for d in os.listdir(KL_O_Dir_Path) if 'icu' in d and '_20_7_30_True' in d]
total_jobs = len(Datasets_Names)
cur_job_index = -1

for dataset_name in Datasets_Names:
    options = create_data_set_params_options(dataset_name)
    # print(len(options))
    for i, op in enumerate(options):
        cur_job_index += 1
        print(f'{dataset_name} - {i + 1}/{len(options)} ETA: {round((total_jobs - cur_job_index)*31/60, 2)} min')
        s = ''
        for l in op:
            s += l
        print(s)

        time.sleep(30)
        change_globals_parameters(op)
        time.sleep(1)
        if validate_changes(op):
            run_job_using_sbatch(sbatch_path, f'{dataset_name} - {i}')

print(get_number_of_jobs('dorpi'))
