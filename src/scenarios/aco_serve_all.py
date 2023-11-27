import json
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Tuple, Union

from api.database import Database
from src.utilities.helper.vrp_helper import vehicle_solution_to_arrivals
from src.utilities.helper.data_helper import get_based_and_load_data, get_google_and_load_data
from src.vrp.ant_colony.aco_hybrid import solve as solve_vrp_aco
from src.vrp.brute_force.brute_force import solve as solve_vrp_bf
from src.tsp.ant_colony.aco_hybrid import solve as solve_tsp_aco
from src.tsp.brute_force.brute_force import solve as solve_tsp_bf
from src.utilities.helper.locations_helper import convert_locations, get_demands_from_locations

DEPOT = 0  # depot
N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def remove_customers_to_be_delayed_and_cancelled(
    vehicle_id: int,
    customers: List[int],
    delay_customers: List[int],
    cancel_customers: List[int],
    cycle: List[int],
) -> None:
    """
    Removes the given customers from the given tour

    :param vehicle_id: ID of the vehicle (for print purposes)
    :param customers: Remaining customers in the VRP tours
    :param delay_customers: Customers to delay orders
    :param cancel_customers: Customers to cancel orders
    :param cycle: A cycle in the vrp solution, i.e. [DEPOT, customer_i, ..., DEPOT]
    """
    customers_to_be_delayed = list(set(cycle) & set(delay_customers))
    for customer in customers_to_be_delayed:
        print(f"Customer {customer} is delayed for the driver {vehicle_id}")
        cycle.remove(customer)
        delay_customers.remove(customer)
    customers_to_be_cancelled = list(set(cycle) & set(cancel_customers))
    for customer in customers_to_be_cancelled:
        print(f"Customer {customer} is cancelled for the driver {vehicle_id}")
        cycle.remove(customer)
        cancel_customers.remove(customer)
        customers.remove(customer)


def run_tsp_algo(
    customers: List[int],
    duration: List[List[List[float]]],
    vehicle_start_time: float,
    vehicle_start_node: int,
    tsp_algo_params: Dict,
) -> List[int]:
    """
    Runs TSP algo on the given customers

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
    elif algo == "aco":
        tsp_sol = solve_tsp_aco(
            duration=duration,
            customers=customers,
            current_time=vehicle_start_time,
            current_location=vehicle_start_node,
            n_hyperparams=tsp_algo_params["n_hyperparams"],
            n_best_results=1,
            is_print_allowed=False,
            ignore_long_trip=False,
        )
        tsp_sol = tsp_sol[0][1]
    elif algo == "sa":
        ...
    elif algo == "ga":
        ...
    else:
        raise "Algo not defined"
    return tsp_sol


def tsp_optimize(
    tsp_freq: int,
    vehicle_id: int,
    vehicle_start_time: float,
    init_cycle: List[int],
    duration: List[List[List[float]]],
    tsp_algo_params: Dict,
) -> List[int]:
    """
    Run TSP optimization on the given customers, considering the tsp frequency

    :param tsp_freq: Frequency of the TSP to run in terms of the number of locations
    :param vehicle_id: ID of the vehicle (for print purposes)
    :param vehicle_start_time: Start time in terms of seconds for the vehicle
    :param init_cycle: The TSP cycle found by the given VRP algorithm
    :param duration: Duration data of NxNx12
    :param tsp_algo_params: Params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit including the vehicle_start_node as the first and DEPOT as the last element
    """
    if tsp_freq <= 0:
        return init_cycle
    init_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [init_cycle], duration)
    init_vehicle_finish_time = init_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} before TSP optimization")
    print(f"Route time: {init_vehicle_finish_time}")
    print(f"Route: {init_cycle}")
    print()
    n_cycle_nodes = len(init_cycle)
    final_cycle = init_cycle.copy()
    for i in range(0, n_cycle_nodes - 3, tsp_freq):
        customers = final_cycle[i + 1 : -1]
        curr_vehicle_start_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle[: i + 1]], duration)
        curr_vehicle_start_time = curr_vehicle_start_times[0][-1]
        print(f"customers={customers} , final_cycle={final_cycle} , i={i}")
        tsp_sol = run_tsp_algo(
            customers=customers,
            duration=duration,
            vehicle_start_time=curr_vehicle_start_time,
            vehicle_start_node=final_cycle[i],
            tsp_algo_params=tsp_algo_params,
        )
        print(f"tsp_sol = {tsp_sol}")
        final_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle], duration)
        final_vehicle_finish_time = final_vehicle_finish_times[0][-1]
        new_vehicle_finish_times = vehicle_solution_to_arrivals(curr_vehicle_start_time, [tsp_sol], duration)
        new_vehicle_finish_time = new_vehicle_finish_times[0][-1]
        improved = new_vehicle_finish_time < final_vehicle_finish_time
        if improved:
            print(f"Partial TSP improvement")
            print(f"Route time: from {final_vehicle_finish_time} to {new_vehicle_finish_time}")
            print(f"Route: from {final_cycle[i:]} to {tsp_sol}")
            final_cycle[i:] = tsp_sol
    final_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle], duration)
    final_vehicle_finish_time = final_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} after TSP optimization")
    print(f"Route time: {final_vehicle_finish_time}")
    print(f"Route: {final_cycle}")
    improved = final_vehicle_finish_time < init_vehicle_finish_time
    print("TSP improvement" if improved else "No improvement")
    print()
    return final_cycle if improved else init_cycle


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
        vrp_sol = solve_vrp_aco(
            k=k,
            q=q,
            duration=duration,
            customers=customers,
            load=demands,
            vehicles_start_times=vehicles_start_times,
            n_hyperparams=vrp_algo_params["n_hyperparams"],
            n_best_results=1,
            optimize_tsp=False,
            ignore_long_trip=False,
            objective_func_type="min_max_time",
            is_print_allowed=False,
        )
        vrp_sol = vrp_sol[0][2]
    elif algo == "sa":
        ...
    elif algo == "ga":
        ...
    else:
        raise "Algo not defined"
    return vrp_sol


def solve_scenario(
    m: int,
    k: int,
    q: int,
    tsp_freq: int,
    customers: List[int],
    delay_customers: List[int],
    cancel_customers: List[int],
    duration: List[List[List[float]]],
    demands: Optional[List[int]],
    vrp_algo_params_path: str = "../../data/scenarios/vrp/config_vrp_aco_1.json",
    tsp_algo_params_path: str = "../../data/scenarios/tsp/config_tsp_bf_1.json",
) -> Tuple[defaultdict, List[float]]:
    """
    Runs the given scenario and simulate the entire day with a couple of VRPs and TSP optimizations for each VRP

    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param tsp_freq: Frequency of the TSP to run in terms of the number of locations
    :param customers: Remaining customers in the VRP tours
    :param delay_customers: Customers to delay orders
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

    vehicles_start_times = [0 for _ in range(m)]
    vehicles_routes = defaultdict(list)
    vehicles_max_time, vehicles_sum_time = 0, 0
    while len(customers) > 0:
        total_demands = 0
        for customer in customers:
            total_demands += demands[customer]
        k_min = (total_demands + q - 1) // q
        k = max(k, k_min)
        min_vehicle_start_times = min(vehicles_start_times)
        available_vehicles = [i for i in range(m) if abs(vehicles_start_times[i] - min_vehicle_start_times) < EPS]
        vrp_sol = run_vrp_algo(
            k=k,
            q=q,
            customers=customers,
            duration=duration,
            demands=demands,
            vehicles_start_times=vehicles_start_times,
            vrp_algo_params=vrp_algo_params,
        )
        print(f"vehicles_routes: {vehicles_routes}")
        print(f"vehicles_start_times: {vehicles_start_times}")
        print(f"customers: {customers}")
        print(f"vrp_sol: {vrp_sol}")
        print("")
        for vehicle_id in available_vehicles:
            if len(vrp_sol[vehicle_id]) > 0:
                cycle = vrp_sol[vehicle_id][0]
                remove_customers_to_be_delayed_and_cancelled(
                    vehicle_id, customers, delay_customers, cancel_customers, cycle
                )
                if cycle == [DEPOT, DEPOT]:
                    continue
                vehicle_start_time = min_vehicle_start_times  # vehicles_start_times[vehicle_id]
                cycle = tsp_optimize(
                    tsp_freq=tsp_freq,
                    vehicle_id=vehicle_id,
                    vehicle_start_time=vehicle_start_time,
                    init_cycle=cycle,
                    duration=duration,
                    tsp_algo_params=tsp_algo_params,
                )
                k -= 1
                vehicles_routes[vehicle_id].append(cycle)
                vehicle_arrivals = vehicle_solution_to_arrivals(vehicle_start_time, [cycle], duration)
                vehicles_start_times[vehicle_id] = vehicle_arrivals[0][-1]
                for customer in cycle[1:-1]:
                    customers.remove(customer)
    for i in range(m):
        vehicles_sum_time += vehicles_start_times[i]
        vehicles_max_time = max(vehicles_max_time, vehicles_start_times[i])
    print("FINAL")
    print(f"vehicles_routes: {vehicles_routes}")
    print(f"vehicles_finish_times: {vehicles_start_times}")
    print(f"vehicles_max_time: {vehicles_max_time}")
    print(f"vehicles_sum_time: {vehicles_sum_time}")
    print(f"customers: {customers}")
    return vehicles_routes, vehicles_start_times


def run(
    n: int = 21,
    m: int = 3,
    k: int = 4,
    q: int = 5,
    tsp_freq: int = 1,
    ignore_customers: List[int] = [1],
    delay_customers: List[int] = [2],
    cancel_customers: List[int] = [3],
    durations_query_row_id: int = 3,
    locations_query_row_id: int = 4,
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
    vrp_algo_params_path: str = "../../data/scenarios/vrp/config_vrp_aco_1.json",
    tsp_algo_params_path: str = "../../data/scenarios/tsp/config_tsp_aco_1.json",
) -> Tuple[defaultdict, List[float]]:
    """
    Runs the given scenario and simulate the entire day with a couple of VRPs and TSP optimizations for each VRP

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param tsp_freq: Frequency of the TSP to run in terms of the number of locations
    :param ignore_customers: Customers to ignore orders
    :param delay_customers: Customers to delay orders
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
    vehicles_routes, vehicles_finish_times = solve_scenario(
        m=m,
        k=k,
        q=q,
        tsp_freq=tsp_freq,
        customers=customers,
        delay_customers=delay_customers,
        cancel_customers=cancel_customers,
        duration=duration,
        demands=load,
        vrp_algo_params_path=vrp_algo_params_path,
        tsp_algo_params_path=tsp_algo_params_path,
    )
    return vehicles_routes, vehicles_finish_times


if __name__ == "__main__":
    run()
