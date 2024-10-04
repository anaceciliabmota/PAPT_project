
class Class:
    def __init__(self, name, number, code, credit, time, center, pre_alocation, index):
        self.name = name
        self.number = number
        self.code = code
        self.credit = credit
        self.time = time
        self.center = center
        self.pre_alocation = pre_alocation
        self.index = index
        

class Professor:
    def __init__(self, name, blocked_time, min_credits, max_credits, daily_max_credits, max_class_days, index):
        self.name = name
        self.blocked_time = blocked_time
        self.min_credits = min_credits
        self.max_credits = max_credits
        self.daily_max_credits = daily_max_credits
        self.max_class_days = max_class_days
        self.index = index
    
    def set_preference(self, preference_list):
        self.preference_list = preference_list

class Data:
    def __init__(self,  list_of_classes, list_of_professors, preferences_dic, penalty_dic):
        self.list_of_classes = list_of_classes
        self.list_of_professors = list_of_professors
        self.preferences_dic = preferences_dic
        self.penalty_dic = penalty_dic
        self.P = range(len(list_of_professors)) # i
        self.T = range(len(list_of_classes)) # j
        self.H = range(96)
        self.D = range(6) #monday to saturday
        self.C = {"CT": 0, "CTDR": 1}
        self.S = [1, 2, 3]
        self.M = 100
        self.shift_time_list = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14, 15]]

