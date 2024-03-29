import datetime
import math
import random
import numpy as np

from collections import defaultdict
from src.tsp.ant_colony.aco_1 import ACO_TSP_1
from src.tsp.ant_colony.aco_2 import ACO_TSP_2
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)
from src.utilities.helper.tsp_helper import route_solution_to_arrivals

from typing import Dict, List, Literal, Optional, Tuple, Union

DEPOT = 0
N_TIME_ZONES = 12  # hours = time slices

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]

RANGE_N_ITERATIONS = (25, 50)
RANGE_N_SUB_ITERATIONS = (5, 10)
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
    best_iter: int,
    route_time: float,
    route: List[int],
    hyperparams: Dict[str, Union[int, float]],
    pheromone_use_first_hour: bool,
    aco_method: str,
) -> None:
    """
    Prints one of the best solutions

    :param result_idx: Rank of the best result among all hyperparameter settings
    :param best_iter: Index of the best tour among iterations
    :param route_time: Total time it takes to visit the locations for the latest driver
    :param route: Sum of the durations of each driver
    :param hyperparams: Hyperparameter settings for the given best tour
    :param pheromone_use_first_hour: Consider first hour of duration data for pheromone calculations
    :param aco_method: Name of the ACO method
    """
    print()
    print(f"Best result: #{result_idx+1}")
    print(f"Best iteration: {best_iter}")
    print(f"ACO method: {aco_method}")
    print(f"Pheromone use first hour: {pheromone_use_first_hour}")
    print(f"Hyperparams: {hyperparams}")
    print(f"Route time: {route_time}")
    print(f"Route: {route}")


def solve(
    duration: List[List[List[float]]],
    load: List[int],
    customers: List[int],
    current_time: float,
    current_location: int,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
    n_hyperparams: int,
    n_best_results: int = 1,
    ignore_long_trip: bool = False,
    aco_sols: List = [ACO_TSP_2],  # [ACO_TSP_1, ACO_TSP_2]
    pheromone_uses_first_hour: List[bool] = [False],  # [False, True]
    range_n_iterations: Tuple[int, int] = RANGE_N_ITERATIONS,
    range_n_sub_iterations: Tuple[int, int] = RANGE_N_SUB_ITERATIONS,
    range_q: Tuple[float, float] = RANGE_Q,
    range_alpha: Tuple[int, int] = RANGE_ALPHA,
    range_beta: Tuple[int, int] = RANGE_BETA,
    range_rho: Tuple[float, float] = RANGE_RHO,
    is_print_allowed: bool = False,
) -> List[Tuple]:
    """
    Try different hyperparamater settings and solve TSP with ACO

    :param duration: Dynamic duration data
    :param load: ...
    :param customers: Customers to be visited
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param do_loading_unloading: ...
    :param cancelled_customers: ...
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_results: Number of best results (hyperparamater settings) to print
    :param ignore_long_trip: Flag to ignore long trips
    :param aco_sols: ACO methods to run
    :param pheromone_uses_first_hour: Flags to consider first hour of duration data for pheromone calculations
    :param is_print_allowed: Flag if print is allowed or not
    :return: Best results
    """
    time_start = datetime.datetime.now()

    n = current_location + 1
    if customers:
        n = max(n, max(customers) + 1)
    if cancelled_customers:
        n = max(n, max(customers) + 1)

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
            for pheromone_use_first_hour in pheromone_uses_first_hour:
                tsp = aco_sol(
                    n=n,
                    pheromone_use_first_hour=pheromone_use_first_hour,
                    ignore_long_trip=ignore_long_trip,
                    customers=customers,
                    start_time=current_time,
                    start_node=current_location,
                    duration=duration,
                    hyperparams=hyperparams,
                )
                route_time, route, best_iter = tsp.solve()
                if best_iter is not None:
                    _, route_time = route_solution_to_arrivals(
                        vehicle_start_time=current_time,
                        route=route,
                        duration=duration,
                        load=load,
                        do_loading_unloading=do_loading_unloading,
                        cancelled_customers=cancelled_customers,
                    )
                    results.append(
                        (
                            route_time,
                            route,
                            best_iter,
                            hyperparams,
                            pheromone_use_first_hour,
                            str(aco_sol),
                        )
                    )
    results.sort(key=lambda x: x[0])

    time_end = datetime.datetime.now()

    for result_idx, result in reversed(list(enumerate(results[:n_best_results]))):
        (
            route_time,
            route,
            best_iter,
            hyperparams,
            pheromone_use_first_hour,
            aco_method,
        ) = result
        if is_print_allowed:
            print_sol(
                result_idx=result_idx,
                best_iter=best_iter,
                route_time=route_time,
                route=route,
                hyperparams=hyperparams,
                pheromone_use_first_hour=pheromone_use_first_hour,
                aco_method=aco_method,
            )

    time_diff = time_end - time_start
    if is_print_allowed:
        print(f"\nTime elapsed = {time_diff.total_seconds()}")

    return results[:n_best_results]


def run_request(
    current_time: float,
    current_location: int,
    customers: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    do_loading_unloading: bool,
    cancelled_customers: List[int],
    n_hyperparams: int = 20,
    aco_sols: Optional[List[str]] = None,
    pheromone_uses_first_hour: Optional[List[bool]] = None,
    range_n_iterations: Optional[List[int]] = None,
    range_n_sub_iterations: Optional[List[int]] = None,
    range_q: Optional[List[float]] = None,
    range_alpha: Optional[List[int]] = None,
    range_beta: Optional[List[int]] = None,
    range_rho: Optional[List[float]] = None,
):
    params = {}
    if aco_sols:
        aco_sols_ = []
        if "ACO_TSP_1" in aco_sols:
            aco_sols_.append(ACO_TSP_1)
        if "ACO_TSP_2" in aco_sols:
            aco_sols_.append(ACO_TSP_2)
        if aco_sols_:
            params["aco_sols"] = aco_sols_
    if pheromone_uses_first_hour:
        params["pheromone_uses_first_hour"] = pheromone_uses_first_hour
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
        duration=duration,
        load=load,
        customers=customers,
        current_time=current_time,
        current_location=current_location,
        do_loading_unloading=do_loading_unloading,
        cancelled_customers=cancelled_customers,
        n_hyperparams=n_hyperparams,
        is_print_allowed=False,
        **params,
    )
    result = results[0]
    result_dict = {
        "route_time": result[0],
        "route": result[1],
    }
    return result_dict


def run(
    n: int = 21,
    aco_sols: List = [ACO_TSP_1, ACO_TSP_2],
    pheromone_uses_first_hour: List[bool] = [False, True],
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    current_time: float = 0,
    current_location: int = DEPOT,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Optional[Dict]:
    """
    Gets input data, try different hyperparamater settings and solve TSP with ACO

    :param n: Number of locations
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param duration_data_type: Type of the duration data to be used
    :return: Best results
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, _ = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, n)
    elif duration_data_type == "google":
        duration, _ = get_google_and_load_data(INPUT_FILES_TIME, None, n)
    else:
        duration, _ = get_based_and_load_data(None, n, per_km_time)
    customers = [i for i in range(1, n) if i != current_location]
    load = [int(i > 0) for i in range(n)]
    result_hyperparams = []
    for aco_sol in aco_sols:
        for use_first_hour in pheromone_uses_first_hour:
            run_durations = []
            run_runtimes = []
            while len(run_durations) < 10:
                time_start = datetime.datetime.now()
                results = solve(
                    duration=duration,
                    load=load,
                    customers=customers,
                    current_time=current_time,
                    current_location=current_location,
                    do_loading_unloading=True,
                    cancelled_customers=[],
                    n_hyperparams=50,
                    n_best_results=1,
                    is_print_allowed=False,
                    aco_sols=[aco_sol],
                    pheromone_uses_first_hour=[use_first_hour],
                )
                if results:
                    time_end = datetime.datetime.now()
                    time_diff = (time_end - time_start).total_seconds()
                    run_runtimes.append(time_diff)
                    result = results[0]
                    run_durations.append(result[0])
                else:
                    print(f"No solution: aco={aco_sol} , pheromonene={use_first_hour}")
            result_hyperparams.append(
                (
                    (aco_sol, use_first_hour),
                    (np.mean(run_durations), np.std(run_durations), np.mean(run_runtimes), np.std(run_runtimes)),
                )
            )
    result_hyperparams.sort(key=lambda x: x[1][0])
    for key, val in result_hyperparams:
        print(f"{key}: {val}")
    return None


if __name__ == "__main__":
    run()
