"""
    Genetic Algorithm method works for both TSP and VRP
    The algorithm can run using a single core or multiple cores
    The program requires the following inputs:
                                            :param multithreaded: (False/True) single core or multi core execution (default is Single Core)
                                            :param N: number of customers
                                            :param W: warehouse 
                                            :param M: number of drivers
                                            :param k: number of cycles
                                            :param q: capacity of vehicle
                                            :param duration: time dependent duration data between nodes
                                            :param load: demand of locations
                                            ??????????????:param ignored_customers: List of customers to be ignored by the algorithm
                                            :param inital_start_times: List of start times for the given number of drivers
"""
import copy

from src.genetic_algorithm.TSP.genetic_algorithm_tsp_sc import run as genetic_algorithm_tsp_sc
#from src.genetic_algorithm.TSP.genetic_algorithm_tsp_mc import run as genetic_algorithm_tsp_mc
#from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc import run as genetic_algorithm_vrp_sc
#from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc_nolib import run as genetic_algorithm_vrp_sc_nolib
from src.genetic_algorithm.TDVRP.further_tests.v2.genetic_algorithm_vrp_mc import run as genetic_algorithm_vrp_mc
#from src.utilities.vrp_helper import get_load_data
from src.utilities.vrp_helper import solution_to_arrivals
#from src.supabase_help.get_supabase_matrix import get_data
#from supabase import create_client, Client



#TODO TEST
#from src.genetic_algorithm.TDVRP.further_tests.SC.genetic_algorithm_vrp_SC import run as test_sc_new
from src.genetic_algorithm.TDVRP.further_tests.SC.good.genetic_algorithm_vrp_SC import run_normal as test_sc_new
import numpy as np
#import math
def get_stats(matrix, k, q):
    sum_all_pairs = []

    for i in range(0, len(matrix)):
        group = []
        for j in range(0, len(matrix[i])):
            group.append(sum(matrix[i][j]))

        group = sum(group)
        sum_all_pairs.append(group)

    sap = np.asarray(sum_all_pairs)
    N = (len(sap)-1)
    # stdev = numpy.std(a = sum_all_pairs, axis = 0, keepdims=True)
    perc = sap / sap.sum()
    perc = perc * 100
    # perc = np.percentile(sap)
    #s_perc = np.asarray(sorted(perc, reverse=False))

    gaps = []
    gaps.append(0)

    for i in range(1, len(perc)-1):
        gaps.append(perc[i + 1] - perc[i])

        #gaps.append([
        #    abs(perc[i] - perc[i-1]),
        #    abs(perc[i+1]-perc[i])
        #])

    # ALONE
    # MID: ALONE OR TOGETHER WITH LOW COST NODES
    # LOW: TOGETHER WITH OTHER LOWS OR MIDS
    orig_perc = copy.deepcopy(perc)

    #min_num_elem_per_cycle = math.ceil(N / k)

    #max_num_elem_per_cycle = q

    alone_nodes = []
    #n_gaps = np.asarray(gaps)

    # set a threshold for having ALONE NODES
    while k * q >= N:#max_num_elem_per_cycle > min_num_elem_per_cycle:
        current_max_selection_index = np.argmax(perc)

        addYN = True
        for i in range(0,len(perc)):
            if i != current_max_selection_index:
                ratio = (perc[current_max_selection_index] / perc[i])
                if not (ratio >= 1.5):
                    addYN = False

        if addYN:
            alone_nodes.append(current_max_selection_index)
            perc[current_max_selection_index] = -1
            #max_num_elem_per_cycle = max_num_elem_per_cycle - 1
            k = k -1
            N = N -1
        else:
            break
    return alone_nodes

def calculate_demand_dict(customer_list, demand_list):

    demand_dict = {}
    demand_dict[0] = 0
    for i in range(0,len(customer_list)):

        demand_dict[customer_list[i]] =  demand_list[i+1]


    return demand_dict

def get_demands(locations, customer_list):
    demand_list = []
    for elem in customer_list:
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

    # k = (sum of demands + q - 1)/q

    demands_sum = sum(demand_list)

    k = (demands_sum + q - 1) // q

    return k

def prepare_ga_inputs(locations, durations, capacities, initial_start_times, ignored_customers, completed_customers,
           multithreaded, random_perm_count, iteration_count, mode, start_node):

    inputs = {}

    #TODO: prepare customer_list
    customer_list = get_customer_list(locations=locations, ignored_customers=ignored_customers, completed_customers=completed_customers)
    inputs["cl"] = customer_list
    # TODO: prepare N
    N = len(customer_list)
    inputs["N"] = N

    #TODO: prepare M
    inputs["M"] = len(capacities)

    #TODO: prepare q
    inputs["q"] = capacities[0]

    #TODO: prepare demands_list
    demand_list = get_demands(locations=locations, customer_list=customer_list)
    demand_list.insert(0,0)
    inputs["load"] = demand_list

    #TODO: prepare k
    inputs["k"] = get_k(q=inputs["q"], demand_list=demand_list)

    #TODO: prepare start_times
    inputs["ist"] = initial_start_times

    #TODO: prepare mode
    inputs["pm"] = mode

    #TODO:prepare sn
    inputs["sn"] = start_node

    return inputs

def prepare_output_format(duration, tours, initial_start_times, map, M, q):

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
                tour.append({"lat": lat, "lng": lng, "arrivalTime": arrival})  # , "node":node
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

#TODO: delete the get_supabase_matrix method and get the data from arin


def map_id_coordinate(json_obj):
    coordinate_index_map = {}
    #TODO: arin json gonderiyor zaten
    for elem in json_obj:
        id = elem["id"]
        lat = elem["lat"]
        lng = elem["lng"]
        coordinate_index_map[id] = {"lat": lat , "lng": lng}

    return coordinate_index_map

def run_GA(locations, durations, capacities, initial_start_times, ignored_customers, completed_customers, multithreaded, random_perm_count, iteration_count, mode, start_node, customers):
    if mode == "TDVRP":
        inputs = prepare_ga_inputs(locations=locations, durations=durations, capacities=capacities, initial_start_times=initial_start_times, ignored_customers=ignored_customers, completed_customers=completed_customers, multithreaded=multithreaded, random_perm_count=random_perm_count, iteration_count=iteration_count, mode=mode, start_node=start_node)

        print("Genetic Algorithm")

        algo_inputs = inputs#["algorithm_inputs"]

        N = algo_inputs["N"] # locations - ignored - completed
        M = algo_inputs["M"] # ok capacities length
        q = algo_inputs["q"] # capaciteler ayni her arabada -> capaties[0]
        k = algo_inputs["k"] if ("k" in algo_inputs) else N/4 # k*q>n-1
        W = 0#algo_inputs["W"] if ("W" in algo_inputs) else 0
        duration =durations#algo_inputs["duration"] # arin veriyor #durations
        multithreaded = multithreaded#algo_inputs["multithreaded"] # arin veriyor default False # multithreaded
        cl = algo_inputs["cl"] # locations - ignored - completed
        sn = algo_inputs["sn"] # tsp icin arinin index api daha hazir degil ama bu gelicek
        load = algo_inputs["load"]# if ("load" in algo_inputs) else get_load_data(input_file_load=None, n=N+1 if cl == [] else len(cl)+1) # locations tablosundan cekicez
        # TODO: prepare LOAD yerine demand_dict gonder
        ist = algo_inputs["ist"] if ("ist" in algo_inputs) else None # arin vericek
        pm = algo_inputs["pm"]

    elif mode == "TSP":
        duration = durations
        ist = [initial_start_times] # here initial start times is a single value
        sn = start_node
        cl = customers
        cl.append(sn) # TODO: cunku sn customer list icinde yok
        multithreaded = multithreaded
        N = len(customers)
        demand_list = get_demands(locations=locations, customer_list=cl)
        demand_list.insert(0, 0)
        load = demand_list
        pm = mode
        W=0
        M=1
        q = len(customers)

    output = None

    #hc_nodes = get_stats(matrix=duration, k = k, q=q)

    #print("CUSTOMER_LIST --->", cl)
    #print("DEMAND_LIST  ---> ",load)

    if pm == "TDVRP":

        if not multithreaded:
            #output = genetic_algorithm_vrp_sc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
            #output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load,ist_in=ist, hc_nodes = hc_nodes)
            output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load,
                                 ist_in=ist, customer_list = cl)

        else:
            # good example
            #output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,demand_in=load, ist_in=ist)

            output = genetic_algorithm_vrp_mc(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load, ist_in=ist, customer_list = cl)

    elif pm == "TSP":

        if not multithreaded:
           #N_in = N, M_in = M, k_in = k, q_in = q, W_in = W, duration_in = duration, demand_in = load, ist_in = ist
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration, demand_in=load,  ist_in=ist, multithreaded=False, start_node = sn, customer_list=cl)
        else:
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist, multithreaded=True,  start_node = sn, customer_list=cl)
            #output = genetic_algorithm_tsp_sc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load,  multithreaded=False)

    #TODO: generate the map information required for the prep out method
    #data = get_supabase_matrix()

    map = map_id_coordinate(locations)
    #TODO: set the inputs etc
    arrivals_final = prepare_output_format(duration=duration, tours=output[2], initial_start_times=ist, map=map, M=M, q=q)
    output_dict = {}
    output_dict["durationMax"] = int(output[0])
    output_dict["durationSum"] = int(output[1])
    output_dict["vehicles"] = arrivals_final
    return output_dict#output[0],output[1], arrivals_final


def run_GA_local_scenario(n, m, k, q, duration, customers, load, vehicle_start_times, mode, start_node, multithreaded):

    if mode == "TDVRP":
        N = n
        M = m
        q = q
        k = k
        W = 0
        duration = duration
        multithreaded = multithreaded
        cl = customers
        sn = start_node
        load = load
        ist = vehicle_start_times
        pm = mode

    elif mode == "TSP":

        N = n
        k = k
        W = 0
        duration = duration
        multithreaded = multithreaded

        cl = customers
        cl.append(start_node)  # TODO: cunku sn customer list icinde yok

        sn = start_node
        load = load
        ist = vehicle_start_times
        pm = mode
        multithreaded = multithreaded

        M = 1
        q = len(customers)

    output = None

    # hc_nodes = get_stats(matrix=duration, k = k, q=q)

    # print("CUSTOMER_LIST --->", cl)
    # print("DEMAND_LIST  ---> ",load)

    if pm == "TDVRP":

        if not multithreaded:
            # output = genetic_algorithm_vrp_sc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
            # output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load,ist_in=ist, hc_nodes = hc_nodes)
            output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load,
                                 ist_in=ist, customer_list=cl)

        else:
            # good example
            # output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,demand_in=load, ist_in=ist)

            output = genetic_algorithm_vrp_mc(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist, customer_list=cl)

    elif pm == "TSP":

        if not multithreaded:
            # N_in = N, M_in = M, k_in = k, q_in = q, W_in = W, duration_in = duration, demand_in = load, ist_in = ist
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist, multithreaded=False, start_node=sn,
                                              customer_list=cl)
        else:
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist, multithreaded=True, start_node=sn,
                                              customer_list=cl)
            # output = genetic_algorithm_tsp_sc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load,  multithreaded=False)

    # TODO: generate the map information required for the prep out method
    # data = get_supabase_matrix()


    return output  # output[0],output[1], arrivals_final