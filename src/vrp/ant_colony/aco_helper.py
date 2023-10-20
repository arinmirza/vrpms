import math
import random
from typing import Dict, Union
from collections import defaultdict

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
    add_depot: bool,
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
    :param add_depot: Flag to add depot as a candidate place to visit next
    :param aco_method: Name of the ACO method
    """
    print()
    print(f"Best result: #{result_idx+1}")
    print(f"Best iteration: {best_iter}")
    print(f"ACO method: {aco_method}")
    print(f"Add depot: {add_depot}")
    print(f"Hyperparams: {hyperparams}")
    print(f"Route max time: {route_max_time}")
    print(f"Route sum time: {route_sum_time}")
    for vehicle_id, vehicle_cycles in vehicle_routes.items():
        print(f"Route of vehicle {vehicle_id}: {vehicle_cycles}")
    for vehicle_id, vehicle_time in vehicle_times.items():
        print(f"Time of vehicle {vehicle_id}: {vehicle_time}")
