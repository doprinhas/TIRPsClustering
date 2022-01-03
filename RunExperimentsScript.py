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

    times = {}

    for dataset_name in Glob.Datasets_Names:

        times['DS_S'] = t.time_ns()  # Dataset Total Time
        Glob.KL_O_Dir_Path = f'{Glob.KL_O_Dir_Path}{dataset_name}/'
        Glob.Results_Dir_Path = f'{Glob.Results_Dir_Path}{dataset_name}/'
        Functions.create_directory(Glob.Results_Dir_Path)
        ent_index_dic = Functions.create_entities_index_dic(Glob.KL_O_Dir_Path)
        pop_size = len(ent_index_dic)

        try:
            Glob.homogeneity_scores = json.load(open(f'{Glob.KL_O_Dir_Path}homogeneity scores.json'))  # TODO: change places
        except:
            Log.write_to_dataset_log('No Entities Homogeneity File')
            print('No Entities Homogeneity File')

        executor = Functions.get_process_pool_executor(1)
        Log.write_dataset_experiments_info(dataset_name)
        Log.write_to_dataset_log(f'Process ID: {os.getpid()}')

        for tirps_size in range(Glob.Min_Tirps_Size, Functions.dataset_max_tirp_size(Glob.KL_O_Dir_Path) + 1)[:1]:

            times['TS_S'] = t.time_ns()
            tirps = Functions.get_tirps(Glob.KL_O_Dir_Path, tirps_size, ent_index_dic)
            Log.write_to_dataset('Parsing TIRPs Size', tirps_size, times["TS_S"])
            output_dir = f'{Glob.Results_Dir_Path}{tirps_size}/'
            Functions.create_directory(output_dir)
            executor.apply_async(Functions.save_coverage, (f'{output_dir}MiningCoverage.txt', tirps))

            for weights in Glob.Prioritize_Metrics_Weights:

                times['W_S'] = t.time_ns()
                candidates = ClusTIRP.pick_candidates(tirps, weights)[:max(Glob.Initial_Cans_Op)]
                Log.write_to_dataset('Picking Candidates', '', times["W_S"])
                Functions.create_candidates_intersection_dictionary([can.tirps[0] for can in candidates])
                Log.write_to_dataset('Picking Candidates and create tirps intersection dictionary', '', times["W_S"])
                clustering_executor = Functions.get_process_pool_executor(10)

                for initial_cans in Glob.Initial_Cans_Op:

                    times['IC_S'] = t.time_ns()
                    output_dir = f'{Glob.Results_Dir_Path}{tirps_size}/' \
                                 f'{Functions.weights_to_dir_name(weights)}/{initial_cans}/'
                    Functions.create_directory(output_dir)
                    Log.set_experiment_logs_path(output_dir)
                    initial_candidates = [can.tirps[0] for can in candidates[:initial_cans]]
                    executor.apply_async(Functions.save_coverage, (f'{output_dir}PossibleCoverage.txt', initial_candidates))
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
                                initial_candidates_copy.pop(0)
                                # solutions.append(ClusTIRP.expand_top_cans(top_candidates[i], set(initial_candidates_copy), weights, top_cans, eps, [i+1]))
                                solutions.append(
                                    clustering_executor.apply_async(ClusTIRP.expand_top_cans, (top_candidates[i],
                                                               set(initial_candidates_copy), weights, top_cans, eps, [i+1]))
                                )
                            solutions = [sol.get() for sol in solutions]

                            Log.write_to_experiment_log(f'Finished Epsilon: {eps} Top Candidates: {top_cans}')
                            solutions.sort(reverse=True, key=lambda sol: sol.score)
                            results[top_cans] = solutions.pop(0)
                            Log.write_to_experiment_times(
                                f'Epsilon: {eps} Top Cans: {top_cans} Time: {Functions.get_time_passed(times["TC_S"], r=5)} min')
                            Log.write_to_dataset_log(f'Finished Top Candidates - {top_cans}')
                            executor.apply_async(Functions.save_solution_tirps, (results[top_cans], Glob.KL_O_Dir_Path, output_dir))

                        Functions.write_results(results, f'{output_dir}{eps}.csv')
                        Log.write_to_dataset('Stopping Criteria', eps, times["E_S"])
                    Log.write_to_dataset('Initial Candidates', initial_cans, times["IC_S"])
                clustering_executor.close()
                Log.write_to_dataset('Prioritize Metric', Functions.weights_to_dir_name(weights), times["W_S"])
            Log.write_to_dataset('TIRPs Size', tirps_size, times["TS_S"])
        # Finished Dataset Experiment
        Log.write_to_dataset('Dataset', dataset_name, times["DS_S"])
        executor.close()
        Log.logs_executor.close()
    print(f'Total Time: {Functions.get_time_passed(times["DS_S"])}')
