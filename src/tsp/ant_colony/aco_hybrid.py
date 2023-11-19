import datetime
import math
import random

from collections import defaultdict
from src.tsp.ant_colony.aco_1 import ACO_TSP_1
from src.tsp.ant_colony.aco_2 import ACO_TSP_2
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)

from typing import Dict, List, Literal, Optional, Tuple, Union

DEPOT = 0
N_TIME_ZONES = 12  # hours = time slices

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
    n: int,
    duration: List[List[List[float]]],
    customers: List[int],
    current_time: float,
    current_location: int,
    n_hyperparams: int,
    n_best_results: int = 1,
    ignore_long_trip: bool = False,
    aco_sols: List = [ACO_TSP_1, ACO_TSP_2],
    pheromone_uses_first_hour: List[bool] = [False, True],
    is_print_allowed: bool = False,
) -> List[Tuple]:
    """
    Try different hyperparamater settings and solve TSP with ACO

    :param n: Number of locations
    :param duration: Dynamic duration data
    :param customers: Customers to be visited
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_results: Number of best results (hyperparamater settings) to print
    :param ignore_long_trip: Flag to ignore long trips
    :param aco_sols: ACO methods to run
    :param pheromone_uses_first_hour: Flags to consider first hour of duration data for pheromone calculations
    :param is_print_allowed: Flag if print is allowed or not
    :return: Best results
    """
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
    n_hyperparams: int = 20,
):
    n = current_location + 1
    if customers:
        n = max(n, max(customers) + 1)
    results = solve(
        n=n,
        duration=duration,
        customers=customers,
        current_time=current_time,
        current_location=current_location,
        n_hyperparams=n_hyperparams,
    )
    result = results[0]
    result_dict = {
        "route_time": result[0],
        "route": result[1],
    }
    return result_dict


def run(
    n: int = 12,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    current_time: float = 0,
    current_location: int = DEPOT,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Dict:
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
    results = solve(
        n=n,
        duration=duration,
        customers=customers,
        current_time=current_time,
        current_location=current_location,
        n_hyperparams=80,
        n_best_results=1,
    )
    result = results[0]
    result_dict = {
        "route_time": result[0],
        "route": result[1],
        "best_iter": result[2],
        "hyperparams": result[3],
        "pheromone_use_first_hour": result[4],
        "aco_method": result[5],
    }
    print(f"result_dict = {result_dict}")
    return result_dict


if __name__ == "__main__":
    run()
