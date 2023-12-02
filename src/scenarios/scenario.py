import datetime
import json
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Tuple, Union

from api.database import Database
from src.utilities2.helper.tsp_helper import route_solution_to_arrivals
from src.utilities2.helper.data_helper import get_based_and_load_data, get_google_and_load_data
#from src.vrp.ant_colony.aco_hybrid import solve as solve_vrp_aco
from src.vrp.brute_force.brute_force import solve as solve_vrp_bf
#from src.tsp.ant_colony.aco_hybrid import solve as solve_tsp_aco
from src.tsp.brute_force.brute_force import solve as solve_tsp_bf
from src.utilities2.helper.locations_helper import convert_locations, get_demands_from_locations
import copy
from src.genetic_algorithm.genetic_algorithm import run_GA_local_scenario as run_ga

DEPOT = 0  # depot
SELF_CYCLE = [DEPOT, DEPOT]

N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def remove_customers_to_be_cancelled(
    vehicle_id: int,
    customers: List[int],
    cancel_customers: List[int],
    cycle: List[int],
) -> List[int]:
    """
    Removes the given customers from the given tour

    :param vehicle_id: ID of the vehicle (for print purposes)
    :param customers: Remaining customers in the VRP tours
    :param cancel_customers: Customers to cancel orders
    :param cycle: A cycle in the vrp solution, i.e. [DEPOT, customer_i, ..., DEPOT]
    :return: customers_to_be_cancelled
    """
    print(f"remove_customers_to_be_cancelled for {vehicle_id}")
    customers_to_be_cancelled = list(set(cycle) & set(cancel_customers))
    for customer in customers_to_be_cancelled:
        print(f"Customer {customer} is cancelled for the driver {vehicle_id}")
        cancel_customers.remove(customer)
    for customer in cycle[1:-1]:
        customers.remove(customer)
    print()
    return customers_to_be_cancelled


def run_tsp_algo(
    customers: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    vehicle_start_time: float,
    vehicle_start_node: int,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
    tsp_algo_params: Dict,
) -> List[int]:
    """
    Runs TSP algo on the given customers

    :param customers: Remaining customers in the TSP cycle
    :param duration: Duration data of NxNx12
    :param load: ...
    :param vehicle_start_time: Start time in terms of seconds for the vehicle
    :param vehicle_start_node: Starting location of the vehicle
    :param do_loading_unloading: ...
    :param cancelled_customers: ...
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
            load=load,
            do_loading_unloading=do_loading_unloading,
            cancelled_customers=cancelled_customers,
            ignore_long_trip=False,
        )
        tsp_sol = tsp_sol[1]
    elif algo == "aco":
        ...
    elif algo == "sa":
        ...
    elif algo == "ga":
        customers_adjusted = copy.deepcopy(customers)

        #if vehicle_start_node != 0 and vehicle_start_node != None: #len(load) <= len(customers):
        #    customers_adjusted.append(vehicle_start_node)
        #    load.append(1)
        #    n = n + 1
        #    q = q + 1

        #load = [1] * len(customers_adjusted)
        #load.insert(0, 0)
        n = len(customers_adjusted)
        q = len(customers_adjusted)*len(customers_adjusted)

        tsp_sol = run_ga(n=len(customers), m=1, k=1, q=q, duration=duration, vehicle_start_times = [vehicle_start_time], mode="TSP", start_node=vehicle_start_node, load = load, multithreaded=True if tsp_algo_params["multithreaded"]=="N" else False, customers=customers_adjusted,do_load_unload=do_loading_unloading, cancelled=cancelled_customers,)
        tsp_sol = (tsp_sol[2][0])
    else:
        raise "Algo not defined"
    return tsp_sol


def tsp_optimize(
    tsp_period: int,
    vehicle_id: int,
    vehicle_start_time: float,
    init_cycle: List[int],
    customers_to_be_cancelled: List[int],
    duration: List[List[List[float]]],
    demands: List[int],
    tsp_algo_params: Dict,
) -> Tuple[List[int], float]:
    """
    Run TSP optimization on the given customers, considering the tsp frequency

    :param tsp_period: Frequency of the TSP to run in terms of the number of locations
    :param vehicle_id: ID of the vehicle (for print purposes)
    :param vehicle_start_time: Start time in terms of seconds for the vehicle
    :param init_cycle: The TSP cycle found by the given VRP algorithm
    :param customers_to_be_cancelled: ...
    :param duration: Duration data of NxNx12
    :param demands: Loads of locations
    :param tsp_algo_params: Params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit including the vehicle_start_node as the first and DEPOT as the last element
    """
    _, init_vehicle_finish_time_with = route_solution_to_arrivals(
        vehicle_start_time, init_cycle, duration, demands, True, customers_to_be_cancelled
    )
    if tsp_period <= 0:
        return init_cycle, init_vehicle_finish_time_with
    _, init_vehicle_finish_time_without = route_solution_to_arrivals(
        vehicle_start_time, init_cycle, duration, demands, True, []
    )
    print(f"Vehicle {vehicle_id} before TSP optimization")
    print(f"Route time (without customers_to_be_cancelled): {init_vehicle_finish_time_without}")
    print(f"Route time (with customers_to_be_cancelled): {init_vehicle_finish_time_with}")
    print(f"Route: {init_cycle}")
    print()
    n_cycle_nodes = len(init_cycle)
    final_cycle = init_cycle.copy()
    for i in range(0, n_cycle_nodes - 3, tsp_period):
        current_cancels = []
        for j in range(i + 1):
            if final_cycle[j] in customers_to_be_cancelled:
                current_cancels.append(final_cycle[j])
        customers = final_cycle[i + 1 : -1]
        _, curr_vehicle_start_time = route_solution_to_arrivals(
            vehicle_start_time, final_cycle[: i + 1], duration, demands, True, []
        )
        print(f"customers={customers} , final_cycle={final_cycle} , i={i}")
        tsp_sol = run_tsp_algo(
            customers=customers,
            duration=duration,
            load=demands,
            vehicle_start_time=curr_vehicle_start_time,
            vehicle_start_node=final_cycle[i],
            do_loading_unloading=False,
            cancelled_customers=current_cancels,
            tsp_algo_params=tsp_algo_params,
        )
        print(f"tsp_sol = {tsp_sol}")
        _, vehicle_finish_time = route_solution_to_arrivals(
            curr_vehicle_start_time, final_cycle[i:], duration, demands, False, current_cancels
        )
        _, new_vehicle_finish_time = route_solution_to_arrivals(
            curr_vehicle_start_time, tsp_sol, duration, demands, False, current_cancels
        )
        improved = new_vehicle_finish_time < vehicle_finish_time
        if improved:
            print(f"Partial TSP improvement")
            print(f"Route time: from {vehicle_finish_time} to {new_vehicle_finish_time}")
            print(f"Route: from {final_cycle[i:]} to {tsp_sol}")
            final_cycle[i:] = tsp_sol
    _, final_vehicle_finish_time = route_solution_to_arrivals(
        vehicle_start_time, final_cycle, duration, demands, True, customers_to_be_cancelled
    )
    print(f"Vehicle {vehicle_id} after TSP optimization")
    print(f"Route time: {final_vehicle_finish_time}")
    print(f"Route: {final_cycle}")
    improved = final_vehicle_finish_time < init_vehicle_finish_time_with
    print("TSP improvement" if improved else "No improvement")
    print()
    return final_cycle, final_vehicle_finish_time


def run_vrp_algo(
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

        # if 0 in customers:# and (customers.count(0) > 1):
        #    customers = [i for i in customers if i != 0]
        # customers.append(0)
        vrp_sol = run_ga(n=len(customers), m=len(vehicles_start_times), k=k, q=q, duration=duration, customers=customers, load=demands,
                         vehicle_start_times=vehicles_start_times, mode="TDVRP", start_node=None,
                         multithreaded=True if vrp_algo_params["multithreaded"] == "Y" else False)
        vrp_sol = vrp_sol[2]
        # run_ga(locations, durations=duration, capacities=[q]*m, initial_start_times=vehicles_start_times, ignored_customers=[], completed_customers=[], multithreaded=True, random_perm_count=0, iteration_count=0, mode="TDVRP", start_node=None, customers=customers)
    else:
        raise "Algo not defined"
    return vrp_sol


def solve_scenario(
    m: int,
    k: int,
    q: int,
    tsp_period: int,
    customers: List[int],
    cancel_customers: List[int],
    duration: List[List[List[float]]],
    demands: Optional[List[int]],
    vrp_algo_params_path: str = "../../data/scenarios/vrp/config_vrp_ga_1.json",
    tsp_algo_params_path: str = "../../data/scenarios/tsp/config_tsp_bf_1.json",
) -> Tuple[defaultdict, List[float], float, float]:
    """
    Runs the given scenario and simulate the entire day with a couple of VRPs and TSP optimizations for each VRP

    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param tsp_period: Frequency of the TSP to run in terms of the number of locations
    :param customers: Remaining customers in the VRP tours
    :param cancel_customers: Customers to cancel orders
    :param duration: Duration data of NxNx12
    :param demands: Demands of the customers
    :param vrp_algo_params_path: Path to the file of params to run VRP algo, it should include "algo" as a key
    :param tsp_algo_params_path: Path to the file of params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit where first and last element of each 1D inner list (cycle) is DEPOT and list
        of vehicle finish times in terms of seconds
    """
    with open(vrp_algo_params_path, "r") as j:
        vrp_algo_params = json.loads(j.read())
    with open(tsp_algo_params_path, "r") as j:
        tsp_algo_params = json.loads(j.read())
    assert "algo" in vrp_algo_params and vrp_algo_params["algo"] in ["bf", "aco", "sa", "ga"], "Invalid vrp json"
    assert "algo" in tsp_algo_params and tsp_algo_params["algo"] in ["bf", "aco", "sa", "ga"], "Invalid tsp json"

    vehicles_times = [0 for _ in range(m)]
    vehicles_routes = defaultdict(list)

    while len(customers) > 0:
        min_vehicle_start_times = min(vehicles_times)
        available_vehicles = [i for i in range(m) if abs(vehicles_times[i] - min_vehicle_start_times) < EPS]
        total_demands = 0
        for customer in customers:
            total_demands += demands[customer]
        k_min = (total_demands + q - 1) // q
        k = max(k, k_min)
        vrp_sol = run_vrp_algo(
            k=k,
            q=q,
            customers=customers,
            duration=duration,
            demands=demands,
            vehicles_start_times=vehicles_times,
            vrp_algo_params=vrp_algo_params,
        )
        print(f"vehicles_routes: {vehicles_routes}")
        print(f"vehicles_times: {vehicles_times}")
        print(f"customers: {customers}")
        print(f"vrp_sol: {vrp_sol}")
        print("")
        for vehicle_id in available_vehicles:
            if len(vrp_sol[vehicle_id]) > 0:
                cycle = vrp_sol[vehicle_id][0]
                if cycle == SELF_CYCLE:
                    continue
                vehicle_start_time = min_vehicle_start_times  # vehicles_times[vehicle_id]
                customers_to_be_cancelled = remove_customers_to_be_cancelled(
                    vehicle_id, customers, cancel_customers, cycle
                )
                cycle, cycle_finish_time = tsp_optimize(
                    tsp_period=tsp_period,
                    vehicle_id=vehicle_id,
                    vehicle_start_time=vehicle_start_time,
                    init_cycle=cycle,
                    customers_to_be_cancelled=customers_to_be_cancelled,
                    duration=duration,
                    demands=demands,
                    tsp_algo_params=tsp_algo_params,
                )
                k -= 1
                vehicles_routes[vehicle_id].append(cycle)
                vehicles_times[vehicle_id] = cycle_finish_time

    vehicles_max_time, vehicles_sum_time = 0, 0
    for i in range(m):
        vehicles_sum_time += vehicles_times[i]
        vehicles_max_time = max(vehicles_max_time, vehicles_times[i])

    print("FINAL")
    print(f"vehicles_max_time: {vehicles_max_time}")
    print(f"vehicles_sum_time: {vehicles_sum_time}")
    for i in range(m):
        print(f"vehicles_times[{i}]: {vehicles_times[i]}")
        print(f"vehicles_route[{i}]: {vehicles_routes[i]}")
    return vehicles_routes, vehicles_times, vehicles_max_time, vehicles_sum_time


def run(
    n: int = 51,
    m: int = 4,
    k: int = 10,
    q: int = 5,
    tsp_period: int = 1,
    ignore_customers: List[int] = [1,3],
    cancel_customers: List[int] = [2,4],
    durations_query_row_id: int = 3,
    locations_query_row_id: int = 1,
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
    vrp_algo_params_path: str = "../../data/scenarios/vrp/config_vrp_ga_1.json",
    tsp_algo_params_path: str = "../../data/scenarios/tsp/config_tsp_ga_1.json",
) -> Tuple[defaultdict, List[float], float, float]:
    """
    Runs the given scenario and simulate the entire day with a couple of VRPs and TSP optimizations for each VRP

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param tsp_period: Frequency of the TSP to run in terms of the number of locations
    :param ignore_customers: Customers to ignore orders
    :param cancel_customers: Customers to cancel orders
    :param durations_query_row_id: Row ID of the "durations" table to be fetched
    :param locations_query_row_id: Row ID of the "locations" table to be fetched
    :param per_km_time: Multiplier to calculate duration from distance in km where duration_data_type = based
    :param input_file_load: Path to the file of demands of customers
    :param duration_data_type: Type of the duration data to be used
    :param vrp_algo_params_path: Path to the file of params to run VRP algo, it should include "algo" as a key
    :param tsp_algo_params_path: Path to the file of params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit where first and last element of each 1D inner list (cycle) is DEPOT and list
        of vehicle finish times in terms of seconds
    """
    start = datetime.datetime.now()
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        errors = []
        database = Database()
        duration = database.get_durations_by_id(durations_query_row_id, errors)
        locations = database.get_locations_by_id(locations_query_row_id, errors)
        new_locations = convert_locations(locations)
        load = get_demands_from_locations(duration, new_locations)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    customers = [i for i in range(1, n) if i not in ignore_customers]
    vehicles_routes, vehicles_finish_times, vehicles_max_time, vehicles_sum_time = solve_scenario(
        m=m,
        k=k,
        q=q,
        tsp_period=tsp_period,
        customers=customers,
        cancel_customers=cancel_customers,
        duration=duration,
        demands=load,
        vrp_algo_params_path=vrp_algo_params_path,
        tsp_algo_params_path=tsp_algo_params_path,
    )
    print("Time elapsed: ", datetime.datetime.now() - start)
    return vehicles_routes, vehicles_finish_times, vehicles_max_time, vehicles_sum_time


if __name__ == "__main__":
    run()
