import itertools
from src.utilities.helper.vrp_helper import get_based_and_load_data
from datetime import datetime
from typing import List, Tuple, Optional

IGNORE_LONG_TRIP = True

INF = float("inf")
N_TIME_ZONES = 12
DEPOT = 0


def calculate_duration(q: int, perm: List[int], duration: List[List[List[float]]], load: List[int]) \
        -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations in order and the route

    :param q: The locations to visit in order
    :param perm: The locations to visit in order
    :param duration: Dynamic duration data of 12xNxN
    :param load: Loads of locations
    :return: Total time it takes to visit the locations in order and the route
    """
    perm = list(perm)
    perm.append(DEPOT)
    last_node = DEPOT
    route = [last_node]
    curr_time, curr_capacity = 0, q

    for node in perm:
        req_capacity = load[node]
        # Ignore DEPOT to DEPOT edge
        if node == DEPOT and last_node == DEPOT:
            continue
        curr_time_slip = int(curr_time / 60)
        if not IGNORE_LONG_TRIP:
            curr_time_slip = min(curr_time_slip, N_TIME_ZONES-1)
        # Fail conditions: time exceeds a day or capacity is not enough
        if curr_time_slip >= N_TIME_ZONES or curr_capacity < req_capacity:
            return INF, None
        curr_time += duration[last_node][node][curr_time_slip]
        if node == DEPOT:  # Go back to the depot and reset the capacity
            curr_capacity = q
        else:  # Deduct the load from the current capacity
            curr_capacity -= req_capacity
        # Add node to the tour
        last_node = node
        route.append(node)

    # Time exceeds a day
    if IGNORE_LONG_TRIP and curr_time >= N_TIME_ZONES*60:
        curr_time, route = INF, None

    return curr_time, route


def solve(n: int, k: int, q: int, duration: List[List[List[float]]], load: List[int]) -> None:
    """
    Solves VRP using brute force

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param duration: Dynamic duration data
    :param load: Loads of locations
    """
    start_time = datetime.now()
    nodes = [i for i in range(1, n)]
    for _ in range(k-1):
        nodes.append(DEPOT)
    best_dist, best_route = INF, None
    # Look for each permutation of visiting orders
    for perm in itertools.permutations(nodes):
        total_dist, route = calculate_duration(q, list(perm), duration, load)
        # Check if it is the best order
        if route is not None and total_dist < best_dist:
            best_dist = total_dist
            best_route = route
    if best_route is None:
        print("No feasible solution")
    else:
        print(f"Total distance: {best_dist}")
        print(f"Best route: {best_route}")
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")


# input_file_load: "../../../data/loads/data_load.txt"
def run(n: int = 8, k: int = 3, q: int = 5, per_km_time: float = 5, input_file_load: Optional[str] = None) -> None:
    """
    Gets dynamic time data of the common dataset and solves VRP using brute force

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    """
    duration, load = get_based_and_load_data(input_file_load, n, per_km_time, True)
    solve(n, k, q, duration, load)


if __name__ == '__main__':
    run()
