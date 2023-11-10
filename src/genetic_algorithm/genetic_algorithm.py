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
from src.genetic_algorithm.TSP.genetic_algorithm_tsp_mc import run as genetic_algorithm_tsp_mc
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc import run as genetic_algorithm_vrp_sc
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc_nolib import run as genetic_algorithm_vrp_sc_nolib
from src.genetic_algorithm.TDVRP.further_tests.v2.genetic_algorithm_vrp_mc import run as genetic_algorithm_vrp_mc
from src.utilities.vrp_helper import get_load_data

#TODO TEST
#from src.genetic_algorithm.TDVRP.further_tests.SC.genetic_algorithm_vrp_SC import run as test_sc_new
from src.genetic_algorithm.TDVRP.further_tests.SC.good.genetic_algorithm_vrp_SC import run as test_sc_new
import numpy as np
import math
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

    while k * q >= N:#max_num_elem_per_cycle > min_num_elem_per_cycle:
        current_max_selection_index = np.argmax(perc)
        alone_nodes.append(current_max_selection_index)
        perc[current_max_selection_index] = -1
        #max_num_elem_per_cycle = max_num_elem_per_cycle - 1
        k = k -1
        N = N -1
    return alone_nodes


def run_GA(inputs):
    print("Genetic Algorithm")

    algo_inputs = inputs["algorithm_inputs"]

    N = algo_inputs["N"]
    M = algo_inputs["M"]
    q = algo_inputs["q"]
    k = algo_inputs["k"] if ("k" in algo_inputs) else N/4
    W = algo_inputs["W"] if ("W" in algo_inputs) else 0
    duration = algo_inputs["duration"]
    multithreaded = algo_inputs["multithreaded"]
    load = algo_inputs["load"] if ("load" in algo_inputs) else get_load_data(input_file_load=None, n=N+1)
    ist = algo_inputs["ist"] if ("ist" in algo_inputs) else None
    pm = inputs["program_mode"]
    
    output = None

    hc_nodes = get_stats(matrix=duration, k = k, q=q)


    if pm == "TDVRP":
        
        if not multithreaded:
            #output = genetic_algorithm_vrp_sc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
            output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load,
                                 ist_in=ist, hc_nodes = hc_nodes)

        else:
            # good example
            #output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,demand_in=load, ist_in=ist)

            output = genetic_algorithm_vrp_mc(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load, ist_in=ist)
    
    elif pm == "TSP":
        
        if not multithreaded:
           #N_in = N, M_in = M, k_in = k, q_in = q, W_in = W, duration_in = duration, demand_in = load, ist_in = ist
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration, demand_in=load,  ist_in=ist, multithreaded=False)
        else:
            output = genetic_algorithm_tsp_sc(N_in=N, M_in=1, k_in=0, q_in=N, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist, multithreaded=True)
            #output = genetic_algorithm_tsp_sc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load,  multithreaded=False)
    
    
    return output