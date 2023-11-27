"""

This script acts as a middleman between the user request and the optimization algorithm

The user has to provide the following information:
0. Program Mode (TDVRP heuristics with Multi Driver Cost Function OR Brute Force TSP with Multi Driver Cost Function OR MapBox new data retrieval command OR ???) {TDVRP/TSP}
1. Customer Coordinates or Addresses
2. Driver Count
3. Warehouse Coordinates or Address --> It is assumed that the warehouse is able to supply any demand
4. The name of the optimization algorithm to be used --> Available options are: Ant Colony Optimization (AC), Genetic Algorithm (GA), Simulated Annealing (SA)
5. Optimization Algorithm Specific Inputs are required --> Genetic Algorithm requires {
                                                                                        :param multithreaded: (False/True) single core or multi core execution (default is Single Core)
                                                                                        :param N: number of customers
                                                                                        :param M: number of drivers
                                                                                        :param k: number of cycles
                                                                                        :param q: capacity of vehicle
                                                                                        :param duration: time dependent duration data between nodes
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
from src.supabase_help.get_supabase_matrix import get_data
from data.travel_time_matrix import main as generate_mapbox_duration_matrix
from src.genetic_algorithm.genetic_algorithm import run_GA

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

def read_saved_duration_matrix():
    return get_data()

def generate_and_save_duration_matrix():
    return generate_mapbox_duration_matrix()

def run_optimization(data_dict):

    output  = {
        "run_successful": False
    }

    program_mode = data_dict["program_mode"]

    if program_mode == "TDVRP":

        duration = get_data()
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
                output.update({"reason": "AC TDVRP optimization did not return any value!"})
                return output

        elif selected_algorithm == "GA":
            result = None

            # TODO: run algo with the correct params

            algo_inputs = data_dict["algorithm_inputs"]

            algo_inputs["duration"] = duration

            result = run_GA(inputs=data_dict)

            if result != None:
                output.update({"run_successful": True})
                output["output"] = result
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "GA TDVRP optimization did not return any value!"})
                return output

        elif selected_algorithm == "SA":
            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "SA TDVRP optimization did not return any value!"})
                return output
        else:
            # return run not successful message
            output.update({"reason": "NO TDVRP heuristic was chosen!"})
            return output

    elif program_mode == "TSP":

        duration = get_data()
        # the SAP data must be read in the below method
        # the parameters of the heuristic functions will be determined accordingly
        # TODO: sap data reading
        # customer_coordinates, driver_count, vehicle_capacity = read_SAP_data()

        selected_algorithm = data_dict["algorithm"]

        # algorithm input should be a nested dictionary in the json dictionary.
        # because the input taken by the algorithms differ
        # TODO: prepare algo input format for each heuristic and tsp
        # algorithm_input = data_dict["algorithm_input"]

        # TODO: parameters
        # N = len(customer_coordinates)

        # M = driver_count

        # Q = vehicle_capacity

        if selected_algorithm == "AC":
            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "AC TSP optimization did not return any value!"})
                return output

        elif selected_algorithm == "GA":

            result = None

            # TODO: run algo with the correct params

            algo_inputs = data_dict["algorithm_inputs"]

            algo_inputs["duration"] = duration

            result = run_GA(inputs=data_dict)

            if result != None:
                output.update({"run_successful": True})
                output["output"] = result
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "GA TSP optimization did not return any value!"})
                return output

        elif selected_algorithm == "SA":
            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "SA TSP optimization did not return any value!"})
                return output

        elif selected_algorithm == "BF":
            result = None

            # TODO: run algo with the correct params

            if result != None:
                output.update({"run_successful": True})
                # TODO: prepare multi driver output and save in the output dictionary
                return output
            else:
                output.update({"reason": "BF TSP optimization did not return any value!"})
                return output

        else:
            # return run not successful message
            output.update({"reason": "NO TSP heuristic or Brute Force was chosen!"})
            return output

    elif program_mode == "UPDATE_DB_CACHE":
        try:
            generate_and_save_duration_matrix()
            output.update({"run_successful": True})
            return output
        except Exception as e:
            output.update({"run_successful": False})
            output.update({"reason": {str(e)}})
            return output


        pass

    else:

        output.update({"reason": "Optimization Mode is not specified! It can either be TDVRP or TSP"})
        return output


def run(user_in):
    # read json data, do other pre-processing and then call run_optimization

    # Example dict format
    # Example dict format

    #data_dict =



    #data_dict = {
    #    "program_mode": "TSP",
    #    "algorithm": "GA"
    #}

    #algo_inputs = {
    #    "N": 15,
    #    "M": 2,
    #    "q": 7,
    #    "k": 3,
    #    "multithreaded": False,
    #}

    # k*q >= n-1


    #data_dict["algorithm_inputs"] = algo_inputs

    # TODO: algorithm_input key will be added

    # TODO: algorithm_input key will be added
    #print(user_in)
    #run_optimization(user_in)

    #return run_optimization(data_dict)

    return run_optimization(user_in)
    #pass
from src.utilities.vrp_helper import solution_to_arrivals
#from src.utilities.helper
from src.supabase_help.get_supabase_matrix import get_data
N_TIME_ZONES = 12  # hours = time slices

def test_solution_to_arrivals(N, tours, vehicle_start_times, map):
    #vehicles_start_times = [10, 20]
    arrivals_updated = []
    solution =[]
    for k, v in tours.items():
        subgroup = []
        for elem in v:
            subgroup.append(elem)
        solution.append(subgroup)

    #solution = [[[0, 1, 2, 0], [0, 3, 4, 0]], [[0, 5, 6, 0], [0, 7, 8, 0]]]
    #expected_arrivals = [[[10, 11, 12, 13], [13, 14, 15, 16]], [[20, 21, 22, 23], [23, 24, 25, 26]]]
    duration = get_data()

    arrivals = solution_to_arrivals(vehicle_start_times, solution, duration)

    arrivals_final = []
    for i in range(0, len(solution)):
        vehicle_tours = []
        for j in range(0, len(solution[i])):
            tour = []
            for k in range(0, len(solution[i][j])):
                node = solution[i][j][k]
                lat = map[node]["lat"]
                lng = map[node]["lng"]
                arrival = arrivals[i][j][k]
                tour.append({"lat":lat , "lng":lng, "arrivalTime":arrival}) # , "node":node
            vehicle_tours.append(tour)
        arrivals_final.append(vehicle_tours)
    print("")
    #assert arrivals == expected_arrivals

#import os
from supabase import create_client, Client
#import supabase_help

def map_id_coordinate(json_obj):
    coordinate_index_map = {}
    #TODO: arin json gonderiyor zaten
    for elem in json_obj["json"]:
        id = elem["id"]
        lat = elem["lat"]
        lng = elem["lng"]
        coordinate_index_map[id] = {"lat": lat , "lng": lng}

    return coordinate_index_map
def get_supabase_matrix():
  url: str = ("https://pkeygmzuwfucblldmkjn.supabase.co")
  key: str = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s")

  supabase: Client = create_client(url, key)

  #with open("dataset_matrix.npy", 'wb+') as f:
    #res = supabase.storage.from_('public/dataset').download("matrix.npy")

  res = supabase.table('locations').select('*').eq('id', 1).execute().data[0]
    #f.write(res)


  return res
  print("res")



if __name__ == "__main__":

    # Example dict format

    data_dict = {
        "program_mode": "TDVRP",
        "algorithm": "GA"
    }

    algo_inputs = {
        "N": 1, #
        "M": 3,
        "q": 6,
        "k": 5,
        "multithreaded": True,
        "cl": [1,2,3,4,5,6,7,8,9,10,11,22,13,14,15,16,17,18,19,20], #
        "sn": None
    }

    # k*q >= n-1

    data_dict["algorithm_inputs"] = algo_inputs

    # TODO: algorithm_input key will be added

    res = run_optimization(data_dict)

    #VST = [0 for _ in range(algo_inputs["M"])]
    #data = get_supabase_matrix()
    #map = map_id_coordinate(data)
    #test_solution_to_arrivals(20, res["output"][2], VST, map)
    pass

