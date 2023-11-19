import datetime
import math
import random

from collections import defaultdict
from src.vrp.ant_colony.aco_1 import ACO_VRP_1
from src.vrp.ant_colony.aco_2 import ACO_VRP_2
from src.tsp.ant_colony.aco_hybrid import solve as solve_aco_tsp
from src.utilities.helper.vrp_helper import vehicle_solution_to_arrivals
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)

from typing import Dict, List, Literal, Optional, Tuple, Union

DEPOT = 0
N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]

RANGE_N_ITERATIONS = (5, 25)
RANGE_N_SUB_ITERATIONS = (2, 5)
RANGE_Q = (1, 1000)
RANGE_ALPHA = (2, 5)
RANGE_BETA = (2, 5)
RANGE_RHO = (0.8, 1)


def get_random_by_log(low: Union[int, float], high: Union[int, float]) -> float:
    """
    Gets a random value in a logarithmic way

    :param low: Lower bound on the random value
    :param high: Upper bound on the random value
    :return: Random value in a logarithmic way
    """
    log_low, log_high = math.log10(low), math.log10(high)
    log_random = random.uniform(log_low, log_high)
    random_value = 10**log_random
    return random_value


def get_hyperparams() -> Dict[str, Union[int, float]]:
    """
    Gets a random hyperparameter settings based on the given ranges
    """
    n_iterations = int(get_random_by_log(RANGE_N_ITERATIONS[0], RANGE_N_ITERATIONS[1]))
    n_sub_iterations = int(get_random_by_log(RANGE_N_SUB_ITERATIONS[0], RANGE_N_SUB_ITERATIONS[1]))
    q = get_random_by_log(RANGE_Q[0], RANGE_Q[1])
    alpha = random.randrange(RANGE_ALPHA[0], RANGE_ALPHA[1] + 1)
    beta = random.randrange(RANGE_BETA[0], RANGE_BETA[1] + 1)
    rho = random.uniform(RANGE_RHO[0], RANGE_RHO[1])
    hyperparams = {
        "N_ITERATIONS": n_iterations,
        "N_SUB_ITERATIONS": n_sub_iterations,
        "Q": q,
        "ALPHA": alpha,
        "BETA": beta,
        "RHO": rho,
    }
    return hyperparams


def print_sol(
    result_idx: int,
    route_max_time: float,
    route_sum_time: float,
    vehicle_routes: defaultdict,
    vehicle_times: defaultdict,
    best_iter: int,
    hyperparams: Dict[str, Union[int, float]],
    consider_depot: bool,
    pheromone_use_first_hour: bool,
    aco_method: str,
) -> None:
    """
    Prints one of the best solutions

    :param result_idx: Rank of the best result among all hyperparameter settings
    :param route_max_time: Total time it takes to visit the locations for the latest driver
    :param route_sum_time: Sum of the durations of each driver
    :param vehicle_routes: The routes for each driver
    :param vehicle_times: The travel duration for each driver
    :param best_iter: Index of the best tour among iterations
    :param hyperparams: Hyperparameter settings for the given best tour
    :param consider_depot: Flag to consider depot as a candidate place to visit next
    :param pheromone_use_first_hour: Consider first hour of duration data for pheromone calculations
    :param aco_method: Name of the ACO method
    """
    print()
    print(f"Best result: #{result_idx+1}")
    print(f"Best iteration: {best_iter}")
    print(f"ACO method: {aco_method}")
    print(f"Consider depot: {consider_depot}")
    print(f"Pheromone use first hour: {pheromone_use_first_hour}")
    print(f"Hyperparams: {hyperparams}")
    print(f"Route max time: {route_max_time}")
    print(f"Route sum time: {route_sum_time}")
    for vehicle_id, vehicle_cycles in vehicle_routes.items():
        print(f"Route of vehicle {vehicle_id}: {vehicle_cycles}")
    for vehicle_id, vehicle_time in vehicle_times.items():
        print(f"Time of vehicle {vehicle_id}: {vehicle_time}")


def tsp_optimize(
    n: int,
    m: int,
    duration: List[List[List[float]]],
    vehicles_start_times: List[float],
    is_print_allowed: bool,
    result: Tuple,
) -> Tuple:
    route_max_time, route_sum_time, vehicle_routes, vehicle_times = result[:4]
    min_vehicle_start_times = min(vehicles_start_times)
    available_vehicles = [i for i in range(m) if abs(vehicles_start_times[i] - min_vehicle_start_times) < EPS]
    improved_vehicles = set()
    for vehicle_id in available_vehicles:
        if vehicle_id in vehicle_routes and len(vehicle_routes[vehicle_id]) > 0:
            vehicle_route = vehicle_routes[vehicle_id][0]
            tsp_sol = solve_aco_tsp(
                n=n,
                duration=duration,
                customers=vehicle_route[1:-1],
                current_time=min_vehicle_start_times,
                current_location=DEPOT,
                is_print_allowed=False,
            )
            arrivals = vehicle_solution_to_arrivals(min_vehicle_start_times, [vehicle_route], duration)
            vrp_sol_route_time = arrivals[0][-1]
            tsp_sol_route_time, tsp_sol_route = tsp_sol[0][0], tsp_sol[0][1]
            if tsp_sol_route_time < vrp_sol_route_time:
                improved_vehicles.add(vehicle_id)
                vehicle_routes[vehicle_id][0] = tsp_sol_route
                if is_print_allowed:
                    print(f"Improved vehicle {vehicle_id}")
                    print(f"TSP Improved from {vrp_sol_route_time} to {tsp_sol_route_time}")
                    print(f"Old TSP cycle: {vehicle_route}")
                    print(f"New TSP cycle: {tsp_sol_route}")
                    print(f"Old finish time for {vehicle_id} = {vehicle_times[vehicle_id]}")
            elif is_print_allowed:
                print(f"No improvement for vehicle {vehicle_id}")
    new_route_max_time, new_route_sum_time, new_vehicle_times = 0, 0, defaultdict(list)
    for vehicle_id in range(m):
        if vehicle_id in improved_vehicles:
            arrivals = vehicle_solution_to_arrivals(min_vehicle_start_times, vehicle_routes[vehicle_id], duration)
            vehicle_time = arrivals[-1][-1]
            if is_print_allowed:
                print(f"New finish time for {vehicle_id} = {vehicle_time}")
        else:
            vehicle_time = vehicle_times[vehicle_id]
        new_route_max_time = max(new_route_max_time, vehicle_time)
        new_route_sum_time += vehicle_time
        new_vehicle_times[vehicle_id] = vehicle_time
    return (
        new_route_max_time,
        new_route_sum_time,
        vehicle_routes,
        new_vehicle_times,
        result[4],
        result[5],
        result[6],
        result[7],
        result[8],
    )


def solve(
    n: int,
    m: int,
    k: int,
    q: int,
    duration: List[List[List[float]]],
    customers: List[int],
    load: Optional[List[int]],
    vehicles_start_times: List[float],
    n_hyperparams: int,
    n_best_results: int = 1,
    optimize_tsp: bool = False,
    ignore_long_trip: bool = False,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_max_time",
    aco_sols: List = [ACO_VRP_1, ACO_VRP_2],
    consider_depots: List[bool] = [False, True],
    pheromone_uses_first_hour: List[bool] = [False, True],
    is_print_allowed: bool = False,
) -> List[Tuple]:
    """
    Try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param duration: Dynamic duration data
    :param load: Loads of locations
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_results: Number of best results (hyperparamater settings) to print
    :param optimize_tsp: Flag to optimize first tours of the vrp solution with TSP
    :param ignore_long_trip: Flag to ignore long trips
    :param customers: List of customers to be ignored by the algorithm
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :param aco_sols: ACO methods to run
    :param consider_depots: Flags to consider depot as a candidate place to visit next
    :param pheromone_uses_first_hour: Flags to consider first hour of duration data for pheromone calculations
    :param is_print_allowed: Flag if print is allowed or not
    :return: Best results
    """
    objective_func_type = objective_func_type.lower()
    assert objective_func_type in [
        "min_max_time",
        "min_sum_time",
    ], f"{objective_func_type} as a function type is not implemented"

    load[DEPOT] = 0

    time_start = datetime.datetime.now()

    all_hyperparams = []
    for _ in range(n_hyperparams):
        hyperparams = get_hyperparams()
        all_hyperparams.append(hyperparams)
        hyperparams_zero = hyperparams.copy()
        hyperparams_zero["Q"], hyperparams_zero["RHO"] = 0, 1
        all_hyperparams.append(hyperparams_zero)

    results = []
    for hyperparams in all_hyperparams:
        for aco_sol in aco_sols:
            for consider_depot in consider_depots:
                for pheromone_use_first_hour in pheromone_uses_first_hour:
                    vrp = aco_sol(
                        n=n,
                        m=m,
                        k=k,
                        q=q,
                        consider_depot=consider_depot,
                        pheromone_use_first_hour=pheromone_use_first_hour,
                        ignore_long_trip=ignore_long_trip,
                        objective_func_type=objective_func_type,
                        customers=customers,
                        vehicles_start_times=vehicles_start_times,
                        duration=duration,
                        load=load,
                        hyperparams=hyperparams,
                    )
                    best_iter, route_max_time, route_sum_time, vehicle_routes, vehicle_times = vrp.solve()
                    if best_iter is not None:
                        results.append(
                            (
                                route_max_time,
                                route_sum_time,
                                vehicle_routes,
                                vehicle_times,
                                best_iter,
                                hyperparams,
                                consider_depot,
                                pheromone_use_first_hour,
                                str(aco_sol),
                            )
                        )
    if objective_func_type == "min_max_time":
        results.sort(key=lambda x: x[0])
    else:
        results.sort(key=lambda x: x[1])

    time_end = datetime.datetime.now()

    if optimize_tsp:
        results[0] = tsp_optimize(n, m, duration, vehicles_start_times, is_print_allowed, results[0])

    if is_print_allowed:
        for result_idx in range(n_best_results):
            print_sol(
                result_idx=result_idx,
                route_max_time=results[result_idx][0],
                route_sum_time=results[result_idx][1],
                vehicle_routes=results[result_idx][2],
                vehicle_times=results[result_idx][3],
                best_iter=results[result_idx][4],
                hyperparams=results[result_idx][5],
                consider_depot=results[result_idx][6],
                pheromone_use_first_hour=results[result_idx][7],
                aco_method=results[result_idx][8],
            )

    time_diff = time_end - time_start
    if is_print_allowed:
        print(f"\nTime elapsed = {time_diff.total_seconds()}")

    return results[:n_best_results]


def run_request(
    q: int,
    duration: List[List[List[float]]],
    load: List[int],
    available_customers: List[int],
    vehicles_start_times: Optional[List[float]],
    n_hyperparams: int,
) -> Dict:
    n = 1
    sum_demand = 0
    for customer in available_customers:
        sum_demand += load[customer]
        n = max(n, customer + 1)
    k = (sum_demand + q - 1) // q
    m = len(vehicles_start_times)
    results = solve(
        n=n,
        m=m,
        k=k,
        q=q,
        duration=duration,
        load=load,
        customers=available_customers,
        vehicles_start_times=vehicles_start_times,
        n_hyperparams=n_hyperparams,
    )
    result = results[0]
    result_dict = {
        "route_max_time": result[0],
        "route_sum_time": result[1],
        "vehicles_routes": result[2],
        "vehicles_times": result[3],
    }
    return result_dict


def run(
    n: int = 12,
    m: int = 2,
    k: int = 3,
    q: int = 5,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Dict:
    """
    Gets input data, try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param input_file_load: Path to the input file including loads (required capacities) of locations
    :param duration_data_type: Type of the duration data to be used
    :return: Best results
    """
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, load = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, n)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    customers = [i for i in range(1, n)]
    vehicles_start_times = [0 for _ in range(m)]
    results = solve(
        n=n,
        m=m,
        k=k,
        q=q,
        duration=duration,
        load=load,
        customers=customers,
        vehicles_start_times=vehicles_start_times,
        n_hyperparams=80,
        n_best_results=1,
    )
    result = results[0]
    result_dict = {
        "route_max_time": result[0],
        "route_sum_time": result[1],
        "vehicle_routes": result[2],
        "vehicle_times": result[3],
        "best_iter": result[4],
        "hyperparams": result[5],
        "consider_depot": result[6],
        "pheromone_use_first_hour": result[7],
        "aco_method": result[8],
    }
    print(f"result_dict = {result_dict}")
    return result_dict


if __name__ == "__main__":
    run()
