from functions import *
from structs import *
from model import *
from model_class import *

filename = "/home/cecilia/Documents/PAPT/AlocacaoProfessoresTurmas2024.2.xlsx"

#filename = "modified_file.xlsx"

list_of_classes, list_of_professors, preferences_map, penalty_map = readFile(filename)

data = Data(list_of_classes, list_of_professors, preferences_map, penalty_map)

model = ModelOptimization()

model.create_model(data)

model.save("model2.lp")

model.solve()

model.save_solution("../solucao.xlsx", data)


