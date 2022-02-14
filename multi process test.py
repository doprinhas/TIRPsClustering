import HelpFunctions as Functions
import Globals as Glob
import time as t


#  32376
for Dataset_Name in ['deb_sax_3_1_10_7_60_True_Gender', 'icu_sax_3_1_20_7_30_True_Gender']:
    st = t.time_ns()
    # Dataset_Name = 'NS_SAHS_300_B_3-4_sax_3_1_30_7_10_True'
    print(Dataset_Name)
    Clusters_Results_Dir_Path = '/home/dorpi/Data/Clusters/'
    KL_O_Dir_Path = "/sise/robertmo-group/Dor/Data/KL Output/"
    Dataset_Path = f'{KL_O_Dir_Path}{Dataset_Name.replace("_Gender", "")}/'
    Results_Dir_Path = f'{Clusters_Results_Dir_Path}{Dataset_Name}/'
    ent_index_dic = Functions.create_entities_index_dic(Dataset_Path)
    # for Tirp_Size in range(2, Functions.dataset_max_tirp_size(Dataset_Path)+1):
    Tirp_Size = 0
    tirps = Functions.get_tirps_multi_thread(Dataset_Path, Tirp_Size, ent_index_dic, 30)
    Functions.save_coverage(f'{Results_Dir_Path}{Tirp_Size}/MiningCoverage.txt', tirps)
    print(f'Finished - TIRP Sized: {Tirp_Size} Time: {Functions.get_time_passed(st, u="sec")} sec')