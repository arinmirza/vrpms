"""

This script acts as a middleman between the user request and the optimization algorithm

The user has to provide the following information:
1. Customer Coordinates or Addresses
2. Driver Count
3. Warehouse Coordinates or Address --> It is assumed that the warehouse is able to supply any demand
4. The name of the optimization algorithm to be used --> Available options are: Ant Colony Optimization, Genetic Algorithm, Simulated Annealing
5. Optimization Algorithm Specific Inputs are required --> Genetic Algorithm requires {multithreaded = True/False}
                                                            Ant Colony Optimization requires {}
                                                            Simulated Annealing requires {}

"""

import json


def read_json(json_input):
    data = open(json_input)
    data_dict = json.load(data)
    return data_dict

