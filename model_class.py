
# to be done: private variables ?
from mip import * 

class ModelOptimization:

    def __init__(self):

        self.m = Model(sense=MAXIMIZE, solver_name = CBC)

    def create_model(self, data):
        
        self.create_binary_variables(data)
        self.create_integer_variables(data)
        self.create_obj_function(data)
        self.create_constraints(data)
        

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
        penalty += self.maximum_credits_penalty(data)
        penalty += self.workdays_penalty(data)
        penalty += self.overload_penalty(data)
        penalty += self.shift_penalty(data)
        penalty += self.work_at_night_penalty(data)
        penalty += self.pre_alocation_penalty(data)

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

    def maximum_credits_penalty(self, data):
        
        penalty = 0
        for i in data.P:
            penalty += data.penalty_dic["max"] * self.g_max[i]

        return penalty

    def workdays_penalty(self, data):
        
        penalty = 0
        for i in data.P:
            penalty += data.penalty_dic["dias"] * self.a_dias[i]
        
        return penalty

    def overload_penalty(self, data):
        
        penalty = 0
        for i in data.P:
            for d in data.D:
                penalty += data.penalty_dic["sobrecarga"] * self.beta[i][d]
        
        return penalty
    
    def shift_penalty(self, data):

        penalty = 0
        for i in data.P:
            for d in data.D: #change to available days per professor
                penalty += data.penalty_dic["turno"] * self.alpha[i][d]

        return penalty

    def work_at_night_penalty(self, data):
        
        penalty = 0
        for i in data.P:
            penalty += self.sigma[i]
        
        penalty = penalty * data.penalty_dic["noturno"]
        return penalty
    
    def pre_alocation_penalty(self, data):

        penalty = 0
        for j in data.T:
            i = data.list_of_classes[j].pre_alocation
            # 1 represents de pre_alocation
            penalty += 1 - self.x[i][j]
        
        penalty = data.penalty_dic["diff"] * penalty
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
    
    def create_constraints(self, data):
        
        self.professor_assignment_constraint(data)
        self.credit_limit_constraint(data)
        self.scheduling_conflit_constraint(data)
        self.credit_limit_day_constraint(data)
        self.professor_day_limit_constraint(data)
        
    def professor_assignment_constraint(self,data):
        # all classes must be assigned to a professor (9)
        
        for j in data.T:
            summation = 0
            
            for i in data.P:
                summation += self.x[i][j]
            
            self.m += summation + self.z[j] == 1 , f"constr(9)({j})"
    
    def credit_limit_constraint(self, data):
        # set credit limit per professor (10)

        for i in data.P:
            professor = data.list_of_professors[i]

            summation = 0
            
            for j in range(len(professor.preference_list)):
                pair = professor.preference_list[j]

                c = data.list_of_classes[pair.class_index]

                summation += c.credit * self.x[i][pair.class_index]
            
            self.m += professor.min_credits - self.g_min[i] <= summation, f"constr(10)({i})(min)"
            self.m += summation <= professor.max_credits + self.g_max[i], f"constr(10)({i})(max)"
    
    def scheduling_conflit_constraint(self, data):
        # ensure that a professor is not assigned to more than one class at the same time. (11)
        
        for i in data.P:
            classes_hour = data.get_classes_hour(i)    

            for h in data.H:
                summation = 0
                valid = False
                for j in classes_hour.keys():
                    if not valid and classes_hour[j][h]:
                        valid = True
                    
                    summation += classes_hour[j][h] * self.x[i][j]

                if valid: 
                    self.m += summation <= 1, f"constr(11)({i})({h})"
    
    def credit_limit_day_constraint(self, data):
        # ensure that a professor don't be assigned to more credits than he could take per day (12)

        for i in data.P:
            classes_hour = data.get_classes_hour(i)

            for d in data.D:
                summation = 0
                valid = False
                for j in classes_hour.keys():
                    w = 0
                    for h in range(16*d, 16*d + 16):
                        if not valid and classes_hour[j][h]:
                            valid = True

                        w += classes_hour[j][h]

                    summation += w * self.x[i][j]
                
                if valid:
                    self.m += summation <= data.list_of_professors[i].daily_max_credits , f"constr(12)({d})({i})"
  
    def professor_day_limit_constraint(self, data):
        # limit the number of days a professor can be allocated for classes. (13)

        for i in data.P:
            summation = 0

            for d in data.D:
                summation += self.y[i][d]
            
            self.m += summation <= data.list_of_professors[i].max_class_days + self.a_dias[i], f"constr(13)({i})"
    
    # def day_availability_constraint(self, data):
    #     # check if a professor is scheduled to teach on a specific day. (14)

    #     for i in data.P:
    #         classes_hour = data.get_classes_hour(i)

    #         for d in data.D:
    #             summation = 0
    #             for j in classes_hour.keys():
                

    def save(self,filename):
        self.m.write(filename)
    #with open(filename, "r") as f: 
        # print(f.read())




