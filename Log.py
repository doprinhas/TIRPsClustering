from datetime import datetime as dt
import Globals as Glob
import HelpFunctions as Functions

import time as t

logs_paths = {  # TODO: initialize all
    'Dataset': '',
    'Current Exp': '',
    'Dataset Times': '',
    'Current Exp Times': ''
}
logs_executor = None


def write_dataset_experiments_info(dataset_name):

    set_dataset_logs_path(f'{Glob.Results_Dir_Path}')

    write_to_dataset_log(f'START! - {dataset_name}')
    write_to_dataset_log(f'\nExperiment Parameters:\n'
                f'TRIPs Size: {Glob.Tirp_Size}\n'
                 f'Initial Candidates: {Glob.Initial_Cans_Op}\n'
                 f'Top Candidates (Top_C): {Glob.Top_Cans_Op}\n'
                 f'Stopping Criteria (epsilon): {Glob.Epsilons_Op}')


def set_dataset_logs_path(dir_path):
    global logs_paths, logs_executor
    exp_st = str(dt.now())[:-7].replace(':', '')
    logs_paths['Dataset'] = f'{dir_path}{exp_st} - Log.txt'
    logs_paths['Dataset Times'] = f'{dir_path}{exp_st} - Times.txt'
    reset_executor()


def set_dataset_times_logs_path(dir_path):
    exp_st = str(dt.now())[:-7].replace(':', '')
    logs_paths['Dataset Times'] = f'{dir_path}{exp_st} - Times.txt'
    reset_executor()


def set_experiment_logs_path(dir_path):
    global logs_paths, logs_executor
    exp_st = str(dt.now())[:-10].replace(':', '')
    logs_paths['Current Exp'] = f'{dir_path}{exp_st} - Log.txt'
    logs_paths['Current Exp Times'] = f'{dir_path}{exp_st} - Times.txt'
    reset_executor()


def reset_executor():
    global logs_executor
    if logs_executor:
        logs_executor.close()
    logs_executor = Functions.get_process_pool_executor(1)


def write_to_dataset(stage, param_value, s_time):
    write_to_dataset_times(f'{stage}: {param_value} Time: {Functions.get_time_passed(s_time, r=5)} min')
    write_to_dataset_log(f'Finished {stage} - {param_value}')


def write_to_dataset_log(line):
    logs_executor.apply_async(write_to_log, (line, logs_paths['Dataset']))


def write_to_experiment_log(line):
    logs_executor.apply_async(write_to_log, (line, logs_paths['Current Exp']))


def write_exp_log():
    log = open(logs_paths['Current Exp'], 'w')
    for line in exp_lines:
        log.write(f'{dt.now()}: {line}\n')
        print(line)
    log.close()


def write_to_dataset_times(line):
    logs_executor.apply_async(write_to_log, (line, logs_paths['Dataset Times']))


def write_to_experiment_times(line):
    logs_executor.apply_async(write_to_log, (line, logs_paths['Current Exp Times']))


def write_to_log(line, path, f='a'):
    log = open(path, f)
    log.write(f'{dt.now()}: {line}\n')
    log.close()
    print(line)


def executor_shutdown(wait=True):
    global logs_executor
    logs_executor.shutdown(wait=wait)