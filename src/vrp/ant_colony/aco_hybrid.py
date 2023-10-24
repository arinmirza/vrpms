import datetime
import math
import random

from collections import defaultdict
from src.vrp.ant_colony.aco_1 import ACO_VRP_1
from src.vrp.ant_colony.aco_2 import ACO_VRP_2
from src.utilities.vrp_helper import get_based_and_load_data, get_google_and_load_data

from typing import Dict, List, Literal, Optional, Tuple, Union

DEPOT = 0
EPS = 1e-6
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes

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
    route_max_time: float,
    route_sum_time: float,
    vehicle_routes: defaultdict,
    vehicle_times: defaultdict,
    hyperparams: Dict[str, Union[int, float]],
    consider_depot: bool,
    pheromone_use_first_hour: bool,
    aco_method: str,
) -> None:
    """
    Prints one of the best solutions

    :param result_idx: Rank of the best result among all hyperparameter settings
    :param best_iter: Index of the best tour among iterations
    :param route_max_time: Total time it takes to visit the locations for the latest driver
    :param route_sum_time: Sum of the durations of each driver
    :param vehicle_routes: The routes for each driver
    :param vehicle_times: The travel duration for each driver
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
    n: int,
    m: int,
    k: int,
    q: int,
    duration: List[List[List[float]]],
    load: Optional[List[int]] = None,
    n_hyperparams: int = 100,
    n_best_results: int = 1,
    ignore_long_trip: bool = False,
    ignored_customers: Optional[List[int]] = None,
    vehicles_start_times: Optional[List[float]] = None,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_sum_time",
    aco_sols: List = [ACO_VRP_1, ACO_VRP_2],
    consider_depots: List[bool] = [False, True],
    pheromone_uses_first_hour: List[bool] = [False, True],
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
    :param ignore_long_trip: Flag to ignore long trips
    :param ignored_customers: List of customers to be ignored by the algorithm
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :param aco_sols: ACO methods to run
    :param consider_depots: Flags to consider depot as a candidate place to visit next
    :param pheromone_uses_first_hour: Flags to consider first hour of duration data for pheromone calculations
    :return: Best results
    """
    objective_func_type = objective_func_type.lower()
    assert objective_func_type in [
        "min_max_time",
        "min_sum_time",
    ], f"{objective_func_type} as a function type is not implemented"

    if load is None:
        load = [1 for _ in range(n)]
        load[DEPOT] = 0

    if vehicles_start_times is None:
        vehicles_start_times = [0 for _ in range(m)]
    else:
        assert len(vehicles_start_times) == m, f"Size of the vehicles_start_times should be {m}"

    if ignored_customers is None:
        ignored_customers = []

    time_start = datetime.datetime.now()

    all_hyperparams = []
    for _ in range(n_hyperparams // 2):
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
                        ignored_customers=ignored_customers,
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

    for result_idx, result in reversed(list(enumerate(results[:n_best_results]))):
        (
            route_max_time,
            route_sum_time,
            vehicle_routes,
            vehicle_times,
            best_iter,
            hyperparams,
            consider_depot,
            pheromone_use_first_hour,
            aco_method,
        ) = result
        print_sol(
            result_idx=result_idx,
            best_iter=best_iter,
            route_max_time=route_max_time,
            route_sum_time=route_sum_time,
            vehicle_routes=vehicle_routes,
            vehicle_times=vehicle_times,
            hyperparams=hyperparams,
            consider_depot=consider_depot,
            pheromone_use_first_hour=pheromone_use_first_hour,
            aco_method=aco_method,
        )

    time_diff = time_end-time_start
    print(f"\nTime elapsed = {time_diff.total_seconds()}")

    return results[:n_best_results]


def run(
    n: int = 10,
    m: int = 2,
    k: int = 10,
    q: int = 3,
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    use_google_data: bool = False,
) -> List[Dict]:
    """
    Gets input data, try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param input_file_load: Path to the input file including loads (required capacities) of locations
    :param use_google_data: Flag to use Google Maps data or not
    :return: Best results
    """
    if use_google_data:
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    results = solve(n=n, m=m, k=k, q=q, duration=duration, load=load, n_hyperparams=10, n_best_results=1)
    results_dict = []
    for result in results:
        (
            route_max_time,
            route_sum_time,
            vehicle_routes,
            vehicle_times,
            best_iter,
            hyperparams,
            consider_depot,
            pheromone_use_first_hour,
            aco_method,
        ) = result
        result_dict = {
            "route_max_time": route_max_time,
            "route_sum_time": route_sum_time,
            "vehicle_routes": vehicle_routes,
            "vehicle_times": vehicle_times,
            "best_iter": best_iter,
            "hyperparams": hyperparams,
            "consider_depot": consider_depot,
            "pheromone_use_first_hour": pheromone_use_first_hour,
            "aco_method": aco_method,
        }
        results_dict.append(result_dict)
    print(results_dict)
    return results_dict


if __name__ == "__main__":
    run()
