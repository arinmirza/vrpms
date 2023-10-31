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
from src.genetic_algorithm.TDVRP.genetic_algorithm_vrp_mc import run as genetic_algorithm_vrp_mc

def run_GA(inputs):
    print("Genetic Algorithm")
    
    N = inputs["N"]
    M = inputs["M"]
    k = inputs["k"]
    q = inputs["q"]
    W = inputs["W"]
    duration = inputs["duration"]
    multithreaded = inputs["multithreaded"]
    load = inputs["load"]
    ist = inputs["inital_start_times"]
    pm = inputs["program_mode"]
    
    output = None
    
    if pm == "TDVRP":
        
        if not multithreaded:
            output = genetic_algorithm_vrp_sc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
        else:
            output = genetic_algorithm_vrp_mc(N=N, M=M, k=k, q=q, W=W, duration=duration, demand=load, ist=ist)
    
    elif pm == "TSP":
        
        if not multithreaded:
            output = genetic_algorithm_tsp_mc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load)
        else:
            output = genetic_algorithm_tsp_sc(N=N, M=1, k=0, q=q, W=W, duration=duration, demand=load)
    
    
    return output