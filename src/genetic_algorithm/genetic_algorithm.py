# Genetic Algorithm Control Script
# Yusuf Serdar Degerli
# TUM MSc Informatics & Management Student
# Interdisciplinary Project with SAP

"""
    Genetic Algorithm method works for both TSP and TDVRP
    The algorithm can run using a single core or multiple cores

"""

from src.genetic_algorithm.TSP.genetic_algorithm_tsp import run as genetic_algorithm_tsp
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp import run as genetic_algorithm_vrp
from src.utilities.utilities1.vrp_helper import solution_to_arrivals
from src.utilities.utilities2.helper import result_2_output
import copy

def calculate_demand_dict_from_locs(locations):

    demand_dict = {}

    for elem in locations:
        demand_dict[elem["id"]] = elem["demand"]

    return demand_dict

def get_demands(locations, customer_list, start_node):
    demand_list = []
    cl = copy.deepcopy(customer_list)
    if start_node != None:
        cl.append(start_node)
    for elem in cl:
        for row in locations:
            if elem == row["id"]:
                demand_list.append(row["demand"])

    return demand_list

def get_customer_list(locations, ignored_customers, completed_customers):
    customer_list = []
    for row in locations:
        if row["id"] not in ignored_customers and row["id"] not in completed_customers and row["id"] != 0:
            customer_list.append(row["id"])

    return customer_list

def get_k(q, demand_list):

    # FORMULA of K: k = (sum of demands + q - 1)/q

    demands_sum = sum(demand_list)

    k = (demands_sum + q - 1) // q

    return k

def prepare_ga_inputs(locations, durations, capacities, initial_start_times, ignored_customers, completed_customers,
           multithreaded, random_perm_count, iteration_count, mode, start_node):

    inputs = {}

    customer_list = get_customer_list(locations=locations, ignored_customers=ignored_customers, completed_customers=completed_customers)
    inputs["cl"] = customer_list

    N = len(customer_list)
    inputs["N"] = N

    inputs["M"] = len(capacities)

    inputs["q"] = capacities[0]

    demand_list = get_demands(locations=locations, customer_list=customer_list, start_node=None)
    demand_list.insert(0,0)
    inputs["load"] = demand_list

    inputs["k"] = get_k(q=inputs["q"], demand_list=demand_list)

    inputs["ist"] = initial_start_times

    inputs["pm"] = mode

    inputs["sn"] = start_node

    return inputs

def prepare_output_format(duration, tours, initial_start_times, map, M, q):

    # Prepares the output data structure which will be used in the UI visualization page

    if initial_start_times is None:
        initial_start_times = [0 for _ in range(M)]

    # group the tours together
    arrivals_updated = []
    solution = []
    for k, v in tours.items():
        subgroup = []
        for elem in v:
            subgroup.append(elem)
        solution.append(subgroup)

    # get the arrival time matrix
    arrivals = solution_to_arrivals(initial_start_times, solution, duration)

    # now add the lat lng information next to the arrival time information
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
                tour.append({"lat": lat, "lng": lng, "arrivalTime": arrival})
            vehicle_tours.append(tour)
        arrivals_final.append(vehicle_tours)

    arrivals_out = []

    for elem in arrivals_final:
        inner_dict = {}
        inner_tours_list = []
        for tour in elem:
            inner_tours_list.append(tour)
        inner_dict["tours"] = inner_tours_list
        inner_dict["capacity"] = q
        arrivals_out.append(inner_dict)

    return arrivals_out

def map_id_coordinate(json_obj):
    coordinate_index_map = {}

    for elem in json_obj:
        id = elem["id"]
        lat = elem["lat"]
        lng = elem["lng"]
        coordinate_index_map[id] = {"lat": lat , "lng": lng}

    return coordinate_index_map

def run_GA(locations, durations, capacities, initial_start_times, ignored_customers, completed_customers, multithreaded,
           random_perm_count, iteration_count, mode, start_node, customers, cancelled_customers, do_load_unload,
           max_k=0,k_lower_limit=True):

    print("Genetic Algorithm")

    # Input Preparation for GA TDVRP or TSP
    if mode == "TDVRP":
        inputs = prepare_ga_inputs(locations=locations, durations=durations, capacities=capacities,
                                   initial_start_times=initial_start_times, ignored_customers=ignored_customers,
                                   completed_customers=completed_customers, multithreaded=multithreaded,
                                   random_perm_count=random_perm_count, iteration_count=iteration_count,
                                   mode=mode, start_node=start_node)

        algo_inputs = inputs
        N = algo_inputs["N"]
        M = algo_inputs["M"]
        q = algo_inputs["q"]
        k = algo_inputs["k"] if ("k" in algo_inputs) else N/4
        W = 0
        duration =durations
        multithreaded = multithreaded
        cl = copy.deepcopy(algo_inputs["cl"])
        sn = algo_inputs["sn"]
        load = algo_inputs["load"]
        demand_dict = calculate_demand_dict_from_locs(locations)
        ist = algo_inputs["ist"] if ("ist" in algo_inputs) else None
        pm = algo_inputs["pm"]

    elif mode == "TSP":
        duration = durations
        ist = [initial_start_times]
        sn = start_node if start_node != None else 0
        cl = copy.deepcopy(customers) # start node must not be included in the customers list
        multithreaded = multithreaded
        N = len(customers)
        demand_list = get_demands(locations=locations, customer_list=cl, start_node=sn)
        demand_list.insert(0, 0)
        load = demand_list
        demand_dict = calculate_demand_dict_from_locs(locations)
        pm = mode
        W=0
        M=1
        q = len(customers)

    if pm == "TDVRP":

        if not k_lower_limit:
            # k_lower_limit equals to False means that max_k can be set by the user

            if max_k == -1 or max_k < k:
                # if user max_k input is -1 -> program will decide
                # program sets the max_k as the double of regular k
                max_k = k*2

                if M*2 > max_k:
                    # depending on the number of vehicles the program changes the max_k
                    max_k = M*2


        if not multithreaded:

            output = genetic_algorithm_vrp(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W,
                                           duration_in=duration, ist_in=ist, customer_list = cl, multithreaded=False,
                                           demand_dict=demand_dict, max_k=max_k,k_lower_limit=k_lower_limit,
                                           population_count=random_perm_count, iteration_count=iteration_count)

        else:

            output = genetic_algorithm_vrp(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, ist_in=ist,
                                           customer_list = cl, multithreaded=True, demand_dict=demand_dict, max_k=max_k,
                                           k_lower_limit=k_lower_limit, population_count=random_perm_count,
                                           iteration_count=iteration_count)

        # TDVRP Output Formatting
        currently_used_vehicle_count = len(output[2].keys())
        sum_time = output[1]
        last_completed_driver_time = output[0]
        output_prep_done = False

        if currently_used_vehicle_count < M:

            while len(output[2].keys()) < M:

                if output[3][len(output[2].keys())] != 0:
                    vst_unused = output[3][len(output[2].keys())]
                    sum_time = output[1] - vst_unused
                    output[3][len(output[2].keys())] = 0
                    output_prep_done = True

                output[2][len(output[2].keys())] = [[]]

        map = map_id_coordinate(locations)
        arrivals_final = prepare_output_format(duration=duration, tours=output[2], initial_start_times=ist, map=map,
                                               M=M, q=q)

        if output_prep_done:
            max = 0
            for elem in list(output[3].keys()):
                if output[3][elem] >= max:
                    max = output[3][elem]

            last_completed_driver_time = max

        output_dict = {}
        output_dict["durationMax"] = int(last_completed_driver_time)
        output_dict["durationSum"] = int(sum_time)
        output_dict["vehicles"] = arrivals_final

    elif pm == "TSP":

        if not multithreaded:
            output = genetic_algorithm_tsp(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, multithreaded=False,
                                           start_node = sn, customer_list=cl, cancelled_customers=cancelled_customers,
                                           do_load_unload=do_load_unload, population_count=random_perm_count,
                                           iteration_count=iteration_count)
        else:
            output = genetic_algorithm_tsp(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, multithreaded=True, start_node = sn,
                                           customer_list=cl, cancelled_customers=cancelled_customers,
                                           do_load_unload=do_load_unload, population_count=random_perm_count,
                                           iteration_count=iteration_count)

        output_dict = result_2_output.tsp_result_2_output(start_time=initial_start_times, start_node=sn, duration=duration, locations=locations, tsp_result={"route":output[2][0]}, load=load, do_loading_unloading=do_load_unload, cancelled_customers=cancelled_customers)
        output_dict["time_diff"] = output[4]

    return output_dict


#######################################################################################################################
#######################################################################################################################
# SCENARIO RUN_GA AND HELPER METHODS

def calculate_demand_dict_from_demand_list(demands):
    demand_dict = {}

    for i in range(0, len(demands)):
        demand_dict[i] = demands[i]

    return demand_dict

def run_GA_local_scenario(n, m, k, q, duration, customers, load, vehicle_start_times, mode, start_node, multithreaded,
                          cancelled=[], do_load_unload=True):
    """
        In real life scenario runs, regular method can be used, this method is used to run the scenearios in local
        environment without the additional input output formatting etc.
    """

    if mode == "TDVRP":

        N = n
        M = m
        q = q
        k = k
        W = 0
        duration = duration
        multithreaded = multithreaded
        cl = copy.deepcopy(customers)
        sn = start_node
        load = load
        ist = vehicle_start_times
        pm = mode
        demand_dict = calculate_demand_dict_from_demand_list(demands=load)

    elif mode == "TSP":

        N = n
        k = 0
        W = 0
        duration = duration
        multithreaded = multithreaded
        cl = copy.deepcopy(customers)
        sn = start_node
        load = load
        ist = vehicle_start_times
        pm = mode
        multithreaded = multithreaded
        demand_dict = calculate_demand_dict_from_demand_list(demands=load)
        M = 1
        # never runs out of capacity, for TSP the capacity constraint is not important
        q = len(customers)*len(customers)

    output = None


    if pm == "TDVRP":

        if not multithreaded:
            output = genetic_algorithm_vrp(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, customer_list=cl,
                                           multithreaded=False,  max_k=k,k_lower_limit=True, population_count=125,
                                           iteration_count=48)
        else:

            output = genetic_algorithm_vrp(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, customer_list=cl,
                                           multithreaded=True, max_k=k,k_lower_limit=True, population_count=125,
                                           iteration_count=48)

    elif pm == "TSP":

        if start_node != 0:
            print('check')

        if not multithreaded:
            # N_in = N, M_in = M, k_in = k, q_in = q, W_in = W, duration_in = duration, demand_in = load, ist_in = ist
            output = genetic_algorithm_tsp(N_in=N, M_in=1, k_in=0, q_in=q, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, multithreaded=False, start_node=sn,
                                           customer_list=cl, cancelled_customers=cancelled, do_load_unload=do_load_unload
                                           ,population_count=125, iteration_count=15)
        else:
            output = genetic_algorithm_tsp(N_in=N, M_in=1, k_in=0, q_in=q, W_in=W, duration_in=duration,
                                           demand_dict=demand_dict, ist_in=ist, multithreaded=True, start_node=sn,
                                           customer_list=cl, cancelled_customers=cancelled, do_load_unload=do_load_unload
                                           ,population_count=125, iteration_count=15)


    return output