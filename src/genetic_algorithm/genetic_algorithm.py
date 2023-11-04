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

from src.genetic_algorithm.TSP.genetic_algorithm_tsp_sc import run as genetic_algorithm_tsp_sc
from src.genetic_algorithm.TSP.genetic_algorithm_tsp_mc import run as genetic_algorithm_tsp_mc
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc import run as genetic_algorithm_vrp_sc
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_sc_nolib import run as genetic_algorithm_vrp_sc_nolib
from src.genetic_algorithm.TDVRP.further_tests.v2.genetic_algorithm_vrp_mc import run as genetic_algorithm_vrp_mc
from src.utilities.vrp_helper import get_load_data

#TODO TEST
#from src.genetic_algorithm.TDVRP.further_tests.SC.genetic_algorithm_vrp_SC import run as test_sc_new
from src.genetic_algorithm.TDVRP.further_tests.SC.good.genetic_algorithm_vrp_SC import run as test_sc_new




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
    
    if pm == "TDVRP":
        
        if not multithreaded:
            output = genetic_algorithm_vrp_sc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
        else:
            output = test_sc_new(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration,
                                              demand_in=load, ist_in=ist)

            #output = genetic_algorithm_vrp_mc(N_in=N, M_in=M, k_in=k, q_in=q, W_in=W, duration_in=duration, demand_in=load, ist_in=ist)
    
    elif pm == "TSP":
        
        if not multithreaded:
            output = genetic_algorithm_tsp_mc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load)
        else:
            output = genetic_algorithm_tsp_sc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load)
    
    
    return output