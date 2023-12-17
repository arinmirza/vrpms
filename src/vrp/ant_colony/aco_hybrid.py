import datetime
import math
import random

from collections import defaultdict
from src.vrp.ant_colony.aco_1 import ACO_VRP_1
from src.vrp.ant_colony.aco_2 import ACO_VRP_2
from src.utilities.helper.vrp_helper import complete_solution_to_arrivals
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)

from typing import Dict, List, Literal, Optional, Tuple, Union

DEPOT = 0
SELF_CYCLE = [DEPOT, DEPOT]

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


def get_hyperparams(
    range_n_iterations: Tuple[int, int] = RANGE_N_ITERATIONS,
    range_n_sub_iterations: Tuple[int, int] = RANGE_N_SUB_ITERATIONS,
    range_q: Tuple[float, float] = RANGE_Q,
    range_alpha: Tuple[int, int] = RANGE_ALPHA,
    range_beta: Tuple[int, int] = RANGE_BETA,
    range_rho: Tuple[float, float] = RANGE_RHO,
) -> Dict[str, Union[int, float]]:
    """
    Gets a random hyperparameter settings based on the given ranges
    """
    n_iterations = int(get_random_by_log(range_n_iterations[0], range_n_iterations[1]))
    n_sub_iterations = int(get_random_by_log(range_n_sub_iterations[0], range_n_sub_iterations[1]))
    q = get_random_by_log(range_q[0], range_q[1])
    alpha = random.randrange(range_alpha[0], range_alpha[1] + 1)
    beta = random.randrange(range_beta[0], range_beta[1] + 1)
    rho = random.uniform(range_rho[0], range_rho[1])
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


def solve(
    k: int,
    q: int,
    duration: List[List[List[float]]],
    customers: List[int],
    load: Optional[List[int]],
    vehicles_start_times: List[float],
    n_hyperparams: int,
    n_best_results: int = 1,
    ignore_long_trip: bool = False,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_max_time",
    aco_sols: List = [ACO_VRP_1, ACO_VRP_2],
    consider_depots: List[bool] = [False, True],
    pheromone_uses_first_hour: List[bool] = [False, True],
    range_n_iterations: Tuple[int, int] = RANGE_N_ITERATIONS,
    range_n_sub_iterations: Tuple[int, int] = RANGE_N_SUB_ITERATIONS,
    range_q: Tuple[float, float] = RANGE_Q,
    range_alpha: Tuple[int, int] = RANGE_ALPHA,
    range_beta: Tuple[int, int] = RANGE_BETA,
    range_rho: Tuple[float, float] = RANGE_RHO,
    is_print_allowed: bool = False,
) -> List[Tuple]:
    """
    Try different hyperparamater settings and solve VRP with ACO

    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param duration: Dynamic duration data
    :param load: Loads of locations
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_results: Number of best results (hyperparamater settings) to print
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

    time_start = datetime.datetime.now()

    load[DEPOT] = 0
    n = 1
    for customer in customers:
        n = max(n, customer + 1)
    m = len(vehicles_start_times)

    all_hyperparams = []
    for _ in range(n_hyperparams):
        hyperparams = get_hyperparams(
            range_n_iterations, range_n_sub_iterations, range_q, range_alpha, range_beta, range_rho
        )
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
                        _, vehicle_times, route_max_time, route_sum_time = complete_solution_to_arrivals(
                            vehicles_start_times=vehicles_start_times,
                            solution=vehicle_routes,
                            duration=duration,
                            load=load,
                        )
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
    print(f"\nTime elapsed = {time_diff.total_seconds()}")

    return results[:n_best_results]


def run_request(
    q: int,
    duration: List[List[List[float]]],
    load: List[int],
    available_customers: List[int],
    vehicles_start_times: Optional[List[float]],
    n_hyperparams: int,
    aco_sols: Optional[List[str]] = None,
    consider_depots: Optional[List[bool]] = None,
    pheromone_uses_first_hour: Optional[List[bool]] = None,
    range_n_iterations: Optional[List[int]] = None,
    range_n_sub_iterations: Optional[List[int]] = None,
    range_q: Optional[List[float]] = None,
    range_alpha: Optional[List[int]] = None,
    range_beta: Optional[List[int]] = None,
    range_rho: Optional[List[float]] = None,
) -> Dict:
    sum_demand = 0
    for customer in available_customers:
        sum_demand += load[customer]
    k = (sum_demand + q - 1) // q
    params = {}
    if aco_sols:
        aco_sols_ = []
        if "ACO_VRP_1" in aco_sols:
            aco_sols_.append(ACO_VRP_1)
        if "ACO_VRP_2" in aco_sols:
            aco_sols_.append(ACO_VRP_2)
        if aco_sols_:
            params["aco_sols"] = tuple(aco_sols_)
    if consider_depots:
        params["consider_depots"] = tuple(consider_depots)
    if pheromone_uses_first_hour:
        params["pheromone_uses_first_hour"] = tuple(pheromone_uses_first_hour)
    if range_n_iterations:
        params["range_n_iterations"] = (range_n_iterations[0], range_n_iterations[1])
    if range_n_sub_iterations:
        params["range_n_sub_iterations"] = (range_n_sub_iterations[0], range_n_sub_iterations[1])
    if range_q:
        params["range_q"] = (range_q[0], range_q[1])
    if range_alpha:
        params["range_alpha"] = (range_alpha[0], range_alpha[1])
    if range_beta:
        params["range_beta"] = (range_beta[0], range_beta[1])
    if range_rho:
        params["range_rho"] = (range_rho[0], range_rho[1])
    results = solve(
        k=k,
        q=q,
        duration=duration,
        load=load,
        customers=available_customers,
        vehicles_start_times=vehicles_start_times,
        n_hyperparams=n_hyperparams,
        is_print_allowed=False,
        **params,
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
    n: int = 51,
    m: int = 4,
    k: int = 10,
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
        k=k,
        q=q,
        duration=duration,
        load=load,
        customers=customers,
        vehicles_start_times=vehicles_start_times,
        n_hyperparams=10,
        n_best_results=1,
    )
    result = results[0]
    result_dict = {
        "route_max_time": result[0],
        "route_sum_time": result[1],
        "vehicles_routes": result[2],
        "vehicles_times": result[3],
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
