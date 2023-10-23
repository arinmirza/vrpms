"""

This script acts as a middleman between the user request and the optimization algorithm

The user has to provide the following information:
0. Program Mode (TDVRP heuristics with Multi Driver Cost Function OR Brute Force TSP with Multi Driver Cost Function OR MapBox new data retrieval command OR ???) {TDVRP/TSP}
1. Customer Coordinates or Addresses
2. Driver Count
3. Warehouse Coordinates or Address --> It is assumed that the warehouse is able to supply any demand
4. The name of the optimization algorithm to be used --> Available options are: Ant Colony Optimization (AC), Genetic Algorithm (GA), Simulated Annealing (SA)
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

from src.genetic_algorithm.genetic_algorithm import run as run_genetic_algorithm
from src.genetic_algorithm.genetic_algorithm_v4_single_core_fast import run as genetic_algorithm_sc_fast
from src.genetic_algorithm.genetic_algorithm_v5_single_core_fastest import run as genetic_algorithm_sc_fastest
from src.genetic_algorithm.genetic_algorithm_v6_multi_core_fast import run as genetic_algorithm_mc_fast

def read_json(json_input):
    data = open(json_input)
    data_dict = json.load(data)
    return data_dict

def read_SAP_data(sap_data):
    """
        SAP data was provided in a previous email.
        JSON
    """
    pass
    # TODO

def read_db_duration_matrix():
    pass
    # TODO

def generate_db_duration_matrix():
    pass
    # TODO

def run_optimization(data_dict):

    output  = {
        "run_successful": False
    }

    program_mode = data_dict["program_mode"]

    if program_mode == "TDVRP":

        # the SAP data must be read in the below method
        # the parameters of the heuristic functions will be determined accordingly
        #TODO: sap data reading
        #customer_coordinates, driver_count, vehicle_capacity = read_SAP_data()

        selected_algorithm = data_dict["algorithm"]

        # algorithm input should be a nested dictionary in the json dictionary.
        # because the input taken by the algorithms differ
        #TODO: prepare algo input format for each heuristic and tsp
        #algorithm_input = data_dict["algorithm_input"]

        # TODO: parameters
        #N = len(customer_coordinates)

        #M = driver_count

        #Q = vehicle_capacity

        if selected_algorithm == "AC":

            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                #TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "AC optimization did not return any value!"})
                return output

        elif selected_algorithm == "GA":

            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "GA optimization did not return any value!"})
                return output

        elif selected_algorithm == "SA":

            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "SA optimization did not return any value!"})
                return output
        else:
            # return run not successful message
            output.update({"reason": "NO TDVRP heuristic was chosen!"})
            return output

    elif program_mode == "TSP":

        pass

    elif program_mode == "UPDATE_DB_CACHE":

        generate_db_duration_matrix()

        pass

    else:

        output.update({"reason": "Optimization Mode is not specified! It can either be TDVRP or TSP"})
        return output


def run():
    # read json data, do other pre-processing and then call run_optimization
    pass

if __name__ == "__main__":

    # Example dict format

    data_dict = {
        "program_mode": "TDVRP",
        "algorithm": "GA"
    }
    # TODO: algorithm_input key will be added

    res = run_optimization(data_dict)

    pass