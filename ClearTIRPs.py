import Globals as Glob
import HelpFunctions as Functions

import time
import os
import shutil
import pandas as pd


def del_file(path):
    if os.path.exists(path):
        print(path)
        os.remove(path)
    else:
        print('del', path)


def get_states(path):
    states_df = pd.read_csv(path)
    return set([str(st) for st in states_df['StateID']])


def get_trips_states(tirp_name):
    states = tirp_name.split(' ')[1]
    return list(states.split('-'))[:-1]


def clear_dir(tirps_files):
    for tirp_name in tirps_files:
        if '.tirp' not in tirp_name:
            continue
        for tirp_state in get_trips_states(tirp_name):
            if tirp_state not in states:
                del_file(f'{Glob.KL_O_Dir_Path}{dataset_name}/{tirp_name}')

for dataset_name in [d for d in os.listdir(Glob.KL_O_Dir_Path) if 'deb' in d and '_10_7_60_True' in d]:

    num_of_threads = 10
    st = time.time_ns()
    tirps_files = os.listdir(f'{Glob.KL_O_Dir_Path}{dataset_name}')
    states = get_states(f'{Glob.KL_O_Dir_Path}{dataset_name}/states.csv')
    num_of_tirps = int(len(tirps_files)/num_of_threads)+1
    executor = Functions.get_thread_pool_executor(num_of_threads)
    for i in range(num_of_threads):
        executor.submit(clear_dir, tirps_files[i*num_of_tirps:(i+1)*num_of_tirps])
    executor.shutdown(wait=True)
    print(f'{dataset_name} Finish Time {Functions.get_time_passed(st)}')

# for tirp_name in tirps_files:
#     if '.tirp' not in tirp_name:
#         continue
#     for tirp_state in get_trips_states(tirp_name):
#         if tirp_state not in states:
#             print(tirp_name)
#             break
#     break
