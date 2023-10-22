"""

This script acts as a middleman between the user request and the optimization algorithm

The user has to provide the following information:
1. Customer Coordinates or Addresses
2. Driver Count
3. Warehouse Coordinates or Address --> It is assumed that the warehouse is able to supply any demand
4. The name of the optimization algorithm to be used --> Available options are: Ant Colony Optimization, Genetic Algorithm, Simulated Annealing
5. Optimization Algorithm Specific Inputs are required --> Genetic Algorithm requires {
                                                                                        :param multithreaded: (True/False) single core or multi core execution
                                                                                        :param N: number of customers
                                                                                        :param M: number of drivers
                                                                                        :param k: number of cycles
                                                                                        :param q: capacity of vehicle
                                                                                        :param distance_data: time dependent duration data between nodes
                                                                                        :param load: demand of locations
                                                                                        :param ignored_customers: List of customers to be ignored by the algorithm
                                                                                        }
                                                            Ant Colony Optimization requires {
                                                                                                :param n: Number of locations
                                                                                                :param m: Max number of vehicles
                                                                                                :param k: Max number of cycles
                                                                                                :param q: Capacity of vehicle
                                                                                                :param duration: Dynamic duration data
                                                                                                :param load: Loads of locations
                                                                                                :param ignored_customers: List of customers to be ignored by the algorithm
                                                                                                }
                                                            Simulated Annealing requires {}

"""

import json


def read_json(json_input):
    data = open(json_input)
    data_dict = json.load(data)
    return data_dict

