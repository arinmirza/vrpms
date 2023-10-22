import itertools
from datetime import datetime
from typing import List, Optional, Tuple

INF = float("inf")
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
DEPOT = 0


def calculate_duration(
    current_time: float,
    current_location: int,
    perm: List[int],
    duration: List[List[List[float]]],
    ignore_long_trip: bool,
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the given order of customers

    :param current_time: Current time
    :param current_location: Current (starting) location
    :param perm: Customers to be visited in order
    :param duration: Dynamic duration data of NxNx12
    :param ignore_long_trip: Flag to ignore long trips
    :return: Total time it takes to visit the locations in the given order and the corresponding route
    """
    route = [current_location]
    route.extend(perm)
    route.append(DEPOT)
    last_node = current_location
    for node in route[1:]:
        hour = int(current_time / TIME_UNITS)
        if not ignore_long_trip:
            hour = min(hour, N_TIME_ZONES - 1)
        if hour >= N_TIME_ZONES:
            return INF, None
        current_time += duration[last_node][node][hour]
        last_node = node
    if ignore_long_trip and current_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, None
    return current_time, route


def solve(
    current_time: float,
    current_location: int,
    customers: List[int],
    duration: List[List[List[float]]],
    ignore_long_trip: bool,
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param current_time: Current time
    :param current_location: Current (starting) location
    :param customers: Customers to be visited
    :param duration: Dynamic duration data of NxNx12
    :param ignore_long_trip: Flag to ignore long trips
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < len(duration), "Current location should be in the fetched duration data"
    start_time = datetime.now()
    best_route_time, best_route = INF, None
    for perm in itertools.permutations(customers):
        route_time, route = calculate_duration(current_time, current_location, list(perm), duration, ignore_long_trip)
        if route_time < best_route_time:
            best_route = route
            best_route_time = route_time
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")
    if best_route is None:
        print("No feasible solution")
    else:
        print(f"Best route time: {best_route_time}")
        print(f"Best route: {best_route}")
    return best_route_time, best_route
