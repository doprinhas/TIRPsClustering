# Python Libraries Imports
import time as t
import os
import pandas as pd
import pickle as pkl
import json
# General Imports
import Globals as Glob
import Log
# Script's Imports
from ClusteringTIRP import ClusteringTIRP
from Solution import Solution
import ClusTIRP
import HelpFunctions as Functions
import Metrics


if __name__ == '__main__':

    times = {'DS_S': t.time_ns()}
    executor = Functions.get_process_pool_executor(1)


    times['PC'] = t.time_ns()
    tirps_names = Functions.get_tirps_files_names(Glob.Dataset_Path, Glob.Tirp_Size)
    Glob.Tirps_Scores = json.load(open(f'{Glob.Dataset_Path}scores.json'))
    Glob.Tirps_Homo_Extra = json.load(open(f'{Glob.Dataset_Path}homo&extra.json'))
    Log.write_dataset_experiments_info(Glob.Dataset_Name)
    t.sleep(1)
    Log.write_to_dataset_log(f'Process ID: {os.getpid()}')
    candidates = ClusTIRP.pick_candidates(tirps_names, Glob.Tirps_Scores, Glob.Tirps_Homo_Extra)
    Log.write_to_dataset('Picking Candidates', '', times["PC"])
    clustering_executor = Functions.get_process_pool_executor(10)

    for initial_cans in Glob.Initial_Cans_Op:

        times['IC_S'] = t.time_ns()
        output_dir = f'{Glob.Results_Dir_Path}{Glob.Tirp_Size}/{initial_cans}/'
        Functions.create_directory(output_dir)
        Log.set_experiment_logs_path(output_dir)

        initial_candidates = [can.tirps[0] for can in candidates[:initial_cans]]
        executor.apply_async(Functions.save_coverage, (f'{output_dir}InitialCansCoverage.txt', initial_candidates))
        Log.write_to_experiment_log(f'Starting...')

        results = {}
        for eps in Glob.Epsilons_Op:
            times['E_S'] = t.time_ns()
            for top_cans in Glob.Top_Cans_Op:

                times['TC_S'] = t.time_ns()
                initial_candidates_copy = list(initial_candidates)
                top_candidates = candidates[:top_cans if top_cans != 'Optimal' else initial_cans]
                Log.write_to_experiment_log(f'Start Epsilon: {eps} Top Candidates: {top_cans}')

                solutions = []
                for i in range(len(top_candidates)):
                    initial_candidates_copy.remove(top_candidates[i].get_first())
                    # solutions.append(ClusTIRP.expand_top_cans(top_candidates[i], set(initial_candidates_copy), top_cans, eps, [i+1]))
                    solutions.append(
                        clustering_executor.apply_async(ClusTIRP.expand_top_cans, (top_candidates[i],
                                                        set(initial_candidates_copy), top_cans, eps, [i+1]))
                    )
                solutions = [sol.get() for sol in solutions]

                Log.write_to_experiment_log(f'Finished Epsilon: {eps} Top Candidates: {top_cans}')
                solutions.sort(reverse=True, key=lambda sol: sol.score)
                results[top_cans] = solutions.pop(0)
                results[top_cans].set_time(Functions.get_time_passed(times["TC_S"], r=5))
                Log.write_to_experiment_times(
                    f'Epsilon: {eps} Top Cans: {top_cans} Time: {Functions.get_time_passed(times["TC_S"], r=5)} min')
                Log.write_to_dataset_log(f'Finished Top Candidates - {top_cans}')
                executor.apply_async(Functions.save_solution_tirps, (results[top_cans], Glob.Dataset_Path, output_dir))

            executor.apply_async(Functions.copy_files, (results[top_cans], Glob.Dataset_Path, output_dir))
            Functions.write_results(results, f'{output_dir}{eps}.csv')
            Log.write_to_dataset('Stopping Criteria', eps, times["E_S"])
        Log.write_to_dataset('Initial Candidates', initial_cans, times["IC_S"])
    clustering_executor.close()
    ent_index_dic = Functions.create_entities_index_dic(f'{Glob.KL_O_Dir_Path}{Glob.Dataset_Name}/')
    tirps = Functions.get_tirps_multi_thread(Glob.Dataset_Path, Glob.Tirp_Size, ent_index_dic)
    executor.apply_async(Functions.save_coverage, (f'{Glob.Results_Dir_Path}{Glob.Tirp_Size}/MiningCoverage.txt', tirps))
    Log.write_to_dataset('Dataset', Glob.Dataset_Name, times["DS_S"])
    executor.close()
    Log.logs_executor.close()
    print(f'Total Time: {Functions.get_time_passed(times["DS_S"])}')

