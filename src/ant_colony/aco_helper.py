import math
import random
from typing import Tuple, Dict, List, Union


def get_random_by_log(low: float, high: float) -> float:
    """
    Gets a random value in a logarithmic way

    :param low: Lower bound on the random value
    :param high: Upper bound on the random value
    :return: Random value in a logarithmic way
    """
    log_low, log_high = math.log10(low), math.log10(high)
    log_random = random.uniform(log_low, log_high)
    random_value = 10 ** log_random
    return random_value


def get_hyperparams(range_n_iterations: Tuple[int, int],
                    range_q: Tuple[float, float],
                    range_alpha: Tuple[int, int],
                    range_beta: Tuple[int, int],
                    range_rho: Tuple[float, float]) -> Dict[str, Union[int, float]]:
    """
    Gets a random hyperparameter settings based on the given ranges

    :param range_n_iterations: Range for the number of iterations that ACO will run
    :param range_q: Range for the trail increment to be used in ACO as a hyperparameter
    :param range_alpha: Range for the relative weight of feedback to be used in ACO as a hyperparameter
    :param range_beta: Range for the relative weight of problem information to be used in ACO as a hyperparameter
    :param range_rho: Range for the forgetting rate to be used in ACO as a hyperparameter
    :return: Random hyperparameter settings based on the given ranges
    """
    n_iterations = random.randrange(range_n_iterations[0], range_n_iterations[1]+1)
    q = get_random_by_log(range_q[0], range_q[1])
    alpha = random.randrange(range_alpha[0], range_alpha[1]+1)
    beta = random.randrange(range_beta[0], range_beta[1]+1)
    rho = random.uniform(range_rho[0], range_rho[1])
    hyperparams = {
        "N_ITERATIONS": n_iterations,
        "Q": q,
        "ALPHA": alpha,
        "BETA": beta,
        "RHO": rho,
    }
    return hyperparams


def print_sol_1(result_idx: int, best_vrp_route_cost: float, best_iter: int, best_vrp_route: List[List[int]],
                hyperparams: Dict[str, Union[int, float]], print_route: bool = False) -> None:
    """
    Prints one of the best solutions

    :param result_idx: Rank of the best result among all hyperparameter settings
    :param best_vrp_route_cost: Total cost of the best tour
    :param best_iter: Index of the best tour among iterations
    :param best_vrp_route: Locations in the best tour, in order
    :param hyperparams: Hyperparameter settings for the given best tour
    :param print_route: Flag to print the best route or not
    """
    print(f"\nBest result: #{result_idx+1}")
    print(f"Hyperparams: {hyperparams}")
    print(f"Best iteration: {best_iter}")
    print(f"Best cost: {best_vrp_route_cost}")
    if print_route and (best_vrp_route is not None):
        for ant_idx, ant_route in enumerate(best_vrp_route):
            if len(ant_route) > 2:
                print(f"Ant {ant_idx}: {ant_route}")


def print_sol_2(result_idx: int, best_vrp_route_cost: float, best_iter: int, best_vrp_route: List[int],
                hyperparams: Dict[str, Union[int, float]], print_route: bool = False) -> None:
    """
    Prints one of the best solutions

    :param result_idx: Rank of the best result among all hyperparameter settings
    :param best_vrp_route_cost: Total cost of the best tour
    :param best_iter: Index of the best tour among iterations
    :param best_vrp_route: Locations in the best tour, in order
    :param hyperparams: Hyperparameter settings for the given best tour
    :param print_route: Flag to print the best route or not
    """
    print(f"\nBest result: #{result_idx+1}")
    print(f"Hyperparams: {hyperparams}")
    print(f"Best iteration: {best_iter}")
    print(f"Best cost: {best_vrp_route_cost}")
    if print_route and (best_vrp_route is not None):
        print(f"VRP {best_vrp_route}")
