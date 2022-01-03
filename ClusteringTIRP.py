import BitVector as bv


class ClusteringTIRP:

    def __init__(self, path, score=None, ent_index_dic=None):
        self.description = ''
        self.file_name = path.split('/')[-1]
        self.score = score
        self.entities = set()
        self.set_tirp(path)
        if ent_index_dic:
            self.ent_vec = bv.BitVector(size=len(ent_index_dic))
            self.init_ent_vec(ent_index_dic)

    def set_tirp(self, path):
        file_lines = open(path).readlines()
        self.set_description(file_lines[0])
        self.set_entities(file_lines[1:])

    def set_description(self, f_line):
        s_line = f_line.split(' ')
        self.description = f'{s_line[1]} {s_line[2]} {s_line[3]}'

    def set_entities(self, lines):
        for line in lines:
            ent = line[:20].split(':')[0]
            self.entities.add(int(ent))

    def set_score(self, score):
        self.score = score

    def init_ent_vec(self, ent_index_dic):
        for ent in self.entities:
            self.ent_vec[ent_index_dic[ent]] = 1

    def population_size(self):
        return self.ent_vec.length()

    def coverage(self):
        return len(self.entities) / self.ent_vec.length()

    def intersection(self, other):
        return self.entities.intersection(other.entities)

    def proportional_intersection(self, other):
        return len(self.intersection(other))/self.population_size()

    def __and__(self, other):
        return self.ent_vec & other.ent_vec

    def __or__(self, other):
        return self.ent_vec | other.ent_vec

    def __xor__(self, other):
        return self.ent_vec ^ other.ent_vec

