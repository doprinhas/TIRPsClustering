import pandas as pd
import numpy as np
import Globals as glob


class TIRPFileParser:

    State_Id_Lbl = 'StateID'
    Prop_Id_Lbl = 'TemporalPropertyID'
    Bin_Low_Lbl = 'BinLow'
    Bin_High_Lbl = 'BinHigh'
    Method_Lbl = 'Method'

    def __init__(self, path, states_path):
        self.entities_tirp_instances = {}
        self.size = 0
        self.states = []
        self.states_dis = []
        self.relations = []
        self.abstraction_method = ''
        self.supporting_entities_num = 0
        self.mean_HS = 0
        self.set_file(path, states_path)
        self.parse_file()

    def set_file(self, path, states_path):
        if '.tirp' not in path:
            raise ValueError
        # self.reset()
        file = open(path)
        self.dis = path.split('/')[-1][2:-5]
        self.file_lines = file.readlines()
        self.states_df = pd.read_csv(states_path, low_memory=False)
        self.abstraction_method = self.states_df[self.Method_Lbl][0]

    def parse_file(self):
        self.parse_first_line(self.file_lines[0])
        self.set_states_dis()
        del self.file_lines[0]
        self.split_entities()
        self.parse_instances()
        del self.file_lines

    def parse_first_line(self, line):
        split_line = line.split(' ')
        self.size = int(split_line[1])
        self.states = split_line[2].split('-')[:-1]
        self.relations = split_line[3].split('.')[:-1]
        self.supporting_entities_num = int(split_line[4])
        self.mean_HS = float(split_line[5])

    def set_states_dis(self):
        for state_Id in self.states:
            query = '{}=={}'.format(self.State_Id_Lbl, state_Id)
            state_record = self.states_df.query(query)
            state_prop_name = glob.rev_props_ids_dic[state_record[self.Prop_Id_Lbl].values[0]]
            low, high = round(state_record[self.Bin_Low_Lbl].values[0], 3), round(state_record[self.Bin_High_Lbl].values[0], 3)
            state_dis = f'{state_prop_name} {low}:{high}'
            self.states_dis.append(state_dis)

    def split_entities(self):
        for line in self.file_lines:
            split_line = line.replace('\n', '').split(':')
            ent = int(split_line[0])
            self.entities_tirp_instances[ent] = split_line[1]

    def parse_instances(self):
        for ent in self.entities_tirp_instances:
            ent_instances = []
            instances = self.entities_tirp_instances[ent].split(';')
            for instance in instances:
                instance_tup = tuple(instance.split(','))
                ent_instances.append(instance_tup)
            self.entities_tirp_instances[ent] = ent_instances

    def get_all_instances(self):
        instances = []
        for ent in self.entities_tirp_instances:
            instances += self.entities_tirp_instances[ent]
        return instances

    def print_states(self):
        for state_id, state_dis in zip(self.states, self.states_dis):
            print(state_id, '-', state_dis)

    def get_tirp_instance(self):
        chosen_instance, min_len = None, float('inf')
        for instance in self.get_all_instances()[:-1]:
            duration = self.calc_instance_len(instance)
            if duration < min_len:
                chosen_instance = instance
                min_len = duration
            if min_len <=100:
                break

        return chosen_instance

    def calc_instance_len(self, instance):
        low, high = int(instance[0].split('-')[0]), int(instance[-1].split('-')[-1])
        return high-low

    def get_tirp_instance_example(self):
        tirp = []
        inst = self.get_tirp_instance()
        min_ts = int(inst[0].split('-')[0])
        for interval_str in self.get_tirp_instance():
            low, high = interval_str.split('-')
            tirp.append((int(low)-min_ts, int(high)-min_ts))
        return tuple(tirp)

    def clac_dur(self, instance):
        st, et = [], []
        for inter in instance:
            low, high = inter.split('-')
            st.append(int(low))
            et.append(int(high))
        return max(et) - min(st)

    def mean_duration(self):
        durations = []
        for instance in self.get_all_instances()[:-1]:
            durations.append(self.clac_dur(instance))
        return np.mean(durations)

    def interval_len(self, interval):
        s, e = [int(v) for v in interval.split('-')]
        return e - s

    def get_general_instance(self):
        all_instances = self.get_all_instances()
        intervals_lengths = [[] for i in range(self.size)]
        intervals_start_offsets = [[] for i in range(self.size)]
        for instance in all_instances:
            t_st = int(instance[0].split('-')[0])
            for interval, intervals_length, intervals_start_offset in zip(instance, intervals_lengths, intervals_start_offsets):
                s, e = [int(v) for v in interval.split('-')]
                intervals_length.append(e - s)
                intervals_start_offset.append(s-t_st)

        instance = []
        for interval_durations, interval_mean_offset in zip(intervals_lengths, intervals_start_offsets):
            s = np.mean(interval_mean_offset)
            e = s + np.mean(interval_durations)
            instance.append((s, e))
        return tuple(instance)




