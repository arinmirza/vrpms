def run_vrp_algo(
    n: int,
    m: int,
    k: int,
    q: int,
    customers: List[int],
    duration: List[List[List[float]]],
    demands: Optional[List[int]],
    vehicles_start_times: List[float],
    vrp_algo_params: Dict,
) -> Union[Dict, List[List[List[int]]]]:
    """
    Runs VRP algo on the given customers

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param customers: Remaining customers in the VRP tours
    :param duration: Duration data of NxNx12
    :param demands: Demands of the customers
    :param vehicles_start_times: Start times in terms of seconds for the vehicles
    :param vrp_algo_params: Params to run VRP algo, it should include "algo" as a key
    :return: List of location ids to visit where first and last element of each 1D inner list (cycle) is DEPOT
    """
    algo = vrp_algo_params["algo"]
    vrp_sol = None
    if algo == "bf":
        vrp_sol = solve_vrp_bf(
            k=k,
            q=q,
            duration=duration,
            load=demands,
            customers=customers,
            vehicles_start_times=vehicles_start_times,
            ignore_long_trip=False,
            objective_func_type="min_max_time",
        )
        vrp_sol = vrp_sol[2]
    elif algo == "aco":

       ...
    elif algo == "sa":
        ...
    elif algo == "ga":
        customers_old = copy.deepcopy(customers)
        #if 0 in customers:# and (customers.count(0) > 1):
        #    customers = [i for i in customers if i != 0]
            #customers.append(0)
        vrp_sol = run_ga(n=n, m=m, k=k, q=q, duration=duration, customers=customers, load=demands, vehicle_start_times=vehicles_start_times, mode="TDVRP", start_node=None, multithreaded= True if vrp_algo_params["multithreaded"]=="Y" else False)
        vrp_sol = vrp_sol[2]
        #run_ga(locations, durations=duration, capacities=[q]*m, initial_start_times=vehicles_start_times, ignored_customers=[], completed_customers=[], multithreaded=True, random_perm_count=0, iteration_count=0, mode="TDVRP", start_node=None, customers=customers)
    else:
        raise "Algo not defined"
    return vrp_sol


def run_tsp_algo(
    n: int,
    customers: List[int],
    duration: List[List[List[float]]],
    vehicle_start_time: float,
    vehicle_start_node: int,
    tsp_algo_params: Dict,
) -> List[int]:
    """
    Runs TSP algo on the given customers

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param customers: Remaining customers in the TSP cycle
    :param duration: Duration data of NxNx12
    :param vehicle_start_time: Start time in terms of seconds for the vehicle
    :param vehicle_start_node: Starting location of the vehicle
    :param tsp_algo_params: Params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit including the vehicle_start_node as the first and DEPOT as the last element
    """
    algo = tsp_algo_params["algo"]
    tsp_sol = None
    if algo == "bf":
        tsp_sol = solve_tsp_bf(
            current_time=vehicle_start_time,
            current_location=vehicle_start_node,
            customers=customers,
            duration=duration,
            ignore_long_trip=False,
        )
        tsp_sol = tsp_sol[1]
        print("tsp")
    elif algo == "aco":
        ...
    elif algo == "sa":
        ...
    elif algo == "ga":
        customers_adjusted = copy.deepcopy(customers)

        if vehicle_start_node != 0 and vehicle_start_node != None: #len(load) <= len(customers):
            customers_adjusted.append(vehicle_start_node)
        #    load.append(1)
        #    n = n + 1
        #    q = q + 1

        load = [1] * len(customers_adjusted)
        load.insert(0, 0)
        n = len(customers_adjusted)
        q = len(customers_adjusted)
        tsp_sol = run_ga(n=n, m=1, k=0, q=q, duration=duration, vehicle_start_times = [vehicle_start_time], mode="TSP", start_node=vehicle_start_node, load = load, multithreaded=True if tsp_algo_params["multithreaded"]=="Y" else False, customers=customers_adjusted)
        tsp_sol = (tsp_sol[2][0])[0]
    else:
        raise "Algo not defined"
    return tsp_sol