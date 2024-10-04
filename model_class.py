
# to be done: private variables ?
from mip import * 

class ModelOptimization:

    def __init__(self):

        self.m = Model(sense=MAXIMIZE, solver_name = CBC)

    def create_model(self, data):
        
        self.create_binary_variables(data)
        self.create_integer_variables(data)
        self.create_obj_function(data)
        

    def create_obj_function(self, data):
        obj = 0
        obj += self.add_benefits(data)
        obj -= self.add_penalties(data)
        self.m.objective = obj

    def add_benefits(self, data):
        
        obj = 0
        
        for i in data.P: 
            professor = data.list_of_professors[i]

            for j in range(len(professor.preference_list)):
                pair = professor.preference_list[j]

                obj += data.preferences_dic[pair.value] * self.x[i][pair.class_index]
            
        return obj
    
    def add_penalties(self, data):

        penalty = 0
        penalty += self.pending_classes_penalty(data)
        penalty += self.minimun_credits_penalty(data)
        return penalty


    def pending_classes_penalty(self, data):
        
        penalty = 0
        for j in data.T:
            penalty += data.penalty_dic["pendente"] * self.z[j]

        return penalty
    
    def minimun_credits_penalty(self, data):
        
        penalty = 0
        for i in data.P:
            penalty += data.penalty_dic["min"] * self.g_min[i]

        return penalty

    def create_binary_variables(self, data):

        self.x = [[self.m.add_var(name=f"x_{i}_{j}", var_type=BINARY) for j in data.T] for i in data.P]
        self.y = [[self.m.add_var(name=f"y_{i}_{d}", var_type= BINARY) for d in data.D] for i in data.P]
        self.z = [self.m.add_var(name=f"z_{j}", var_type=BINARY) for j in data.T]
        self.alpha = [[self.m.add_var(name=f"alpha_{i}_{k}", var_type=BINARY)for k in data.D] for i in data.P] #afternoon shift
        self.lamb = [[[[self.m.add_var(name=f"lamb_{i}_{k}_{d}_{s}", var_type=BINARY) for s in data.S] for d in data.D] for k in data.C.values()] for i in data.P]


    def create_integer_variables(self, data):

        self.a_dias = [self.m.add_var(name=f"a_dias_{i}", var_type=INTEGER) for i in data.P]
        self.beta = [[self.m.add_var(name=f"beta_{i}_{d}", var_type=INTEGER) for d in data.D] for i in data.P]
        self.g_min = [self.m.add_var(name=f"g_min_{i}", var_type=INTEGER) for i in data.P]
        self.g_max = [self.m.add_var(name=f"g_max_{i}", var_type=INTEGER) for i in data.P]
        self.sigma = [self.m.add_var(name=f"sigma_{i}", var_type=INTEGER) for i in data.P]

    def save(self,filename):
        self.m.write(filename)
    #with open(filename, "r") as f: 
        # print(f.read())




