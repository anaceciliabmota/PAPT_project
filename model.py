from mip import * 

def save(model, filename):
  model.write(filename)
  #with open(filename, "r") as f: 
    # print(f.read())
  
def print_model(model):
    # Imprime a função objetivo
    print("OBJECTIVE FUNCTION: ")
    print(model.objective)

    # Imprime as restrições com seus nomes
    print("\nSUBJECT TO: ")
    for c in model.constrs:
        print(c)



# necessary to change de professors classes representation to not repeat code


def modelling(list_of_classes, list_of_professors, preferences_dic, penalty_dic):
  m = Model(sense=MAXIMIZE, solver_name = CBC)

  P = range(len(list_of_professors)) # i
  T = range(len(list_of_classes)) # j
  H = range(96)
  D = range(6) #monday to saturday
  C = {"CT": 0, "CTDR": 1}
  S = [1, 2, 3]
  M = 100

  shift_time_list = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14, 15]]


  ### VARIABLES ### 

  # BINARY VARIABLES

  x = [[m.add_var(name=f"x_{i}_{j}", var_type=BINARY) for j in T] for i in P]

  y = [[m.add_var(name=f"y_{i}_{d}", var_type= BINARY) for d in D] for i in P]

  z = [m.add_var(name=f"z_{j}", var_type=BINARY) for j in T]

  alpha = [[m.add_var(name=f"alpha_{i}_{k}", var_type=BINARY)for k in D] for i in P] #afternoon shift

  lamb = [[[[m.add_var(name=f"lamb_{i}_{k}_{d}_{s}", var_type=BINARY) for s in S] for d in D] for k in C.values()] for i in P]

  # INTEGER VARIABLES

  a_dias = [m.add_var(name=f"a_dias_{i}", var_type=INTEGER) for i in P]

  beta = [[m.add_var(name=f"beta_{i}_{d}", var_type=INTEGER) for d in D] for i in P]

  g_min = [m.add_var(name=f"g_min_{i}", var_type=INTEGER) for i in P]

  g_max = [m.add_var(name=f"g_max_{i}", var_type=INTEGER) for i in P]

  sigma = [m.add_var(name=f"sigma_{i}", var_type=INTEGER) for i in P]

  ### OBJECTIVE FUNCTION ###

  obj = 0

  # Maximizing professor satisfaction (1)
  
  for i in P: 
    professor = list_of_professors[i]

    for j in range(len(professor.preference_list)):
      pair = professor.preference_list[j]

      obj += preferences_dic[pair.value] * x[i][pair.class_index]
  
  penalty = 0

  # pending classes (2)

  for j in T:
    penalty += penalty_dic["pendente"] * z[j]

  obj -= penalty

  penalty = 0

  # minimun credits (3)

  for i in P:
    penalty += penalty_dic["min"] * g_min[i]
  
  obj -= penalty

  penalty = 0

  # maximun credits (3)

  for i in P:
    penalty += penalty_dic["max"] * g_max[i]

  obj -= penalty

  penalty = 0

  # workdays (4)

  for i in P:
    penalty += penalty_dic["dias"] * a_dias[i]

  obj -= penalty

  penalty = 0

  # overload (5)

  for i in P:
    for d in D:
      penalty += penalty_dic["sobrecarga"] * beta[i][d]

  obj -= penalty

  penalty = 0

  # shift - skip afternoon (6)

  # how do i know the available days per professor??

  for i in P:
    for d in D: #change to available days per professor
      penalty += penalty_dic["turno"] * alpha[i][d]

  obj -= penalty

  penalty = 0

  # work at night (7)

  for i in P:
    penalty += sigma[i]

  penalty = penalty * penalty_dic["noturno"]

  obj -= penalty

  penalty = 0

  # pre alocation (8)

  for j in T:
    i = list_of_classes[j].pre_alocation
    # one represents de pre_alocation
    penalty += 1 - x[i][j]

  obj -= penalty_dic["diff"] * penalty


  m.objective = obj

  ### CONSTRAINTS ###

  # all classes must be assigned to a professor (9)

  for j in T:
    summation = 0
    
    for i in P:
      summation += x[i][j]
    
    m += summation + z[j] == 1 , f"constr(9)({j})"
  

  # set credit limit per professor (10)

  for i in P:
    professor = list_of_professors[i]

    summation = 0
    
    for j in range(len(professor.preference_list)):
      pair = professor.preference_list[j]

      c = list_of_classes[pair.class_index]

      summation += c.credit * x[i][pair.class_index]
     
    m += professor.min_credits - g_min[i] <= summation, f"constr(10)({i})(min)"
    m += summation <= professor.max_credits + g_max[i], f"constr(10)({i})(max)"
  
  # ensure that a professor is not assigned to more than one class at the same time. (11)

  for i in P:
    preference_list = list_of_professors[i].preference_list

    classes_hour = {}
    for pref in preference_list:
      c = list_of_classes[pref.class_index]
      classes_hour[c.index] = c.time

    
      
    # each line of the classes_hour matrix is a class j
    # each column of the classes_hour matrix is a hour (ex: first column is 2M1)
    for h in H:
      summation = 0
      for j in classes_hour.keys():
        summation += classes_hour[j][h] * x[i][j]
      m += summation <= 1, f"constr(11)({i})({h})"

  # ensure that a professor don't be assigned to more credits than he could take per day (12)

  for i in P:
    preference_list = list_of_professors[i].preference_list
    
    classes_hour = {}
    for pref in preference_list:
      c = list_of_classes[pref.class_index]
      classes_hour[c.index] = c.time
    
   

    for d in D:
      summation = 0
      for j in classes_hour.keys():
          w = 0
          for h in range(16*d, 16*d + 16):
            w += classes_hour[j][h]
          
          summation += w * x[i][j]
      
      m += summation <= list_of_professors[i].daily_max_credits , f"constr(12)({d})({i})"
  
  # limit the number of days a professor can be allocated for classes. (13)

  for i in P:
    summation = 0
  
    for d in D:
      summation += y[i][d]
    
    m += summation <= list_of_professors[i].max_class_days + a_dias[i], f"constr(13)({i})"
  
  # check if a professor is scheduled to teach on a specific day. (14)

  for i in P:
    preference_list = list_of_professors[i].preference_list
    
    classes_hour = {}
    for pref in preference_list:
      c = list_of_classes[pref.class_index]
      classes_hour[c.index] = c.time
    
    for d in D:
      summation = 0
      for j in classes_hour.keys():
          w = 0
          for h in range(16*d, 16*d + 16):
            w += classes_hour[j][h]
          
          if w != 0: # the class j is in day d
            summation += x[i][j]
      
      m+= summation <= M * y[i][d], f"constr(14)({i})({d})"
  
  # ensure that a professor is not scheduled at a non available time. (15)

  # to be done
            
  # determine if professor i will be teaching at center k on day d during shift s. (16)

  for i in P:
    preference_list = list_of_professors[i].preference_list

    classes_hour = {}

    for pref in preference_list:
      c = list_of_classes[pref.class_index]
      classes_hour[c.index] = c.time
    
    for d in D: # to be done: change to professor  available days

      for k_name, k in C.items():

        for s in S:
          shift_index = s-1

          summation = 0;

          for j in classes_hour.keys():
            c = list_of_classes[j]

            if c.center == k_name:

              w = 0

              for h in shift_time_list[shift_index]:
                w += classes_hour[j][h + (16 * d)]
              
              if w > 0: #There is class j during that shift on that day
                summation += x[i][j]
          
          m += summation <= M * lamb[i][k][d][shift_index] , f"constr(16)({i})({k_name})({d})({s})"
  
  # ensure that a professor will not be scheduled in more than one center in the same shift. (17)

  for i in P:

    for s in S:
    
      for d in D:
        summation = 0

        for k in C.values():
          summation += lamb[i][k][d][s-1]
        
        m += summation <= 1, f"constr(17)({i})({s})({d})"

  # prevents a professor from teaching classes in the morning if they have taught classes the night before. (18)

  for i in P:
    for d in range(len(D)-1): #to be done: change to professor available days 
      # verify if really is this range
      sum_night = 0
      sum_morning = 0

      for k in C.values(): 
        sum_night += lamb[i][k][d][3-1]
        sum_morning += lamb[i][k][d+1][1-1]
      
      m += sum_night + sum_morning <= 1 + beta[i][d], f"constr(18)({i})({d})"
  
  # ensure a professor is scheduled for consecutive shifts. (19)

  for i in P:
    for d in D: #to be done: change to professor available days 

      sum_morning = 0
      sum_afternoon = 0
      sum_night = 0

      for k in C.values():
        sum_morning += lamb[i][k][d][1-1]
        sum_afternoon += lamb[i][k][d][2-1]
        sum_night += lamb[i][k][d][3-1]
      
      m += sum_morning + sum_night <= 1 + sum_afternoon + alpha[i][d], f"constr(19)({i})({d})"

  # Minimize the number of night shifts scheduled for a professor. (20)

  for i in P:
    summation = 0

    for k in C.values():
      
      for d in D:  #to be done: change to professor available days 

        summation += lamb[i][k][d][3-1]

    m += summation == sigma[i]

  return m

def shift_time(hours): # hour is a number representing the number of different times and days is the amount of days
  
  shift = [[],[],[]]

  for h in range(hours):
    if h % 16 < 6:
      shift[0].append(h)
    elif h % 16 >= 6 and h % 16 < 12:
      shift[1].append(h)
    else:
      shift[2].append(h) 
  
  return shift

def solve(model):
  status = model.optimize()

  print("Status = ", status)
  print(f"Solution value  = {model.objective_value:.2f}\n")

  print("Solution:")
  for v in model.vars:
      print(f"{v.name} = {v.x:.2f}")
