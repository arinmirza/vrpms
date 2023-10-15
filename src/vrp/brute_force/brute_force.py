import itertools
from collections import defaultdict
from datetime import datetime
from queue import PriorityQueue
from typing import List, Literal, Optional, Tuple

IGNORE_LONG_TRIP = True

INF = float("inf")
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
DEPOT = 0


def calculate_duration(
    q: int,
    m: int,
    cycles: List[List[int]],
    duration: List[List[List[float]]],
    load: List[int],
    vehicles_start_times: List[float],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given list of cycles

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param cycles: The cycles to be assigned where one cycle is demonstrated as [DEPOT, c_i, ..., c_j, DEPOT]
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    vehicle_routes = defaultdict(list)
    vehicle_times = defaultdict(float)

    vehicles = PriorityQueue()
    for i in range(m):
        vehicles.put((vehicles_start_times[i], i))
    for cycle in cycles:
        vehicle = vehicles.get()
        vehicle_t, vehicle_id = vehicle
        curr_time = vehicle_t
        last_node = DEPOT
        curr_capacity = q
        for node in cycle[1:]:
            curr_capacity -= load[node]
            if curr_capacity < 0:
                return INF, INF, None, None
            curr_time_slip = int(curr_time / TIME_UNITS)
            if not IGNORE_LONG_TRIP:
                curr_time_slip = min(curr_time_slip, N_TIME_ZONES - 1)
            if curr_time_slip >= N_TIME_ZONES:
                return INF, INF, None, None
            curr_time += duration[last_node][node][curr_time_slip]
            last_node = node
        vehicles.put((curr_time, vehicle_id))
        vehicle_routes[vehicle_id].append(cycle)

    route_max_time = 0
    route_sum_time = 0
    while not vehicles.empty():
        vehicle = vehicles.get()
        vehicle_t, vehicle_id = vehicle
        vehicle_times[vehicle_id] = vehicle_t
        route_max_time = vehicle_t
        route_sum_time += vehicle_t

    if IGNORE_LONG_TRIP and route_max_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, INF, None, None

    return route_max_time, route_sum_time, vehicle_routes, vehicle_times


def calculate_duration_perm(
    q: int,
    m: int,
    perm: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    vehicles_start_times: List[float],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given permutation of nodes

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param perm: The locations to visit in order
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    perm = list(perm)
    perm.append(DEPOT)

    cycles = []
    last_cycle = []
    for node in perm:
        if node == DEPOT:
            if len(last_cycle) > 0:
                cycle = [DEPOT]
                cycle.extend(last_cycle)
                cycle.append(DEPOT)
                cycles.append(cycle)
            last_cycle = []
        else:
            last_cycle.append(node)

    return calculate_duration(q, m, cycles, duration, load, vehicles_start_times)


def solve(
    n: int,
    k: int,
    q: int,
    m: int,
    duration: List[List[List[float]]],
    load: List[int],
    ignored_customers: Optional[List[int]],
    vehicles_start_times: Optional[List[float]],
    objective_func_type: Literal["min_max_time", "min_sum_time"],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Solves VRP using brute force and gets total time it takes to visit the locations for the latest driver, sum of the
        durations of each driver and the routes for each driver

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param ignored_customers: List of customers to be ignored by the algorithm
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :return: Among the all possible routes, total time it takes to visit the locations for the latest driver, sum of the
        durations of each driver, the routes for each driver and the travel duration for each driver
    """
    objective_func_type = objective_func_type.lower()
    assert objective_func_type in [
        "min_max_time",
        "min_sum_time",
    ], f"{objective_func_type} as a function type is not implemented"

    if vehicles_start_times is None:
        vehicles_start_times = [0 for _ in range(m)]
    else:
        assert len(vehicles_start_times) == m, f"Size of the vehicles_start_times should be {m}"

    start_time = datetime.now()

    nodes = []
    for i in range(1, n):
        if ignored_customers is None or i not in ignored_customers:
            nodes.append(i)
    for _ in range(k - 1):
        nodes.append(DEPOT)

    best_route_max_time, best_route_sum_time, best_vehicle_routes, best_vehicle_times = INF, INF, None, None
    # Look for each permutation of visiting orders
    for perm in itertools.permutations(nodes):
        route_max_time, route_sum_time, vehicle_routes, vehicle_times = calculate_duration_perm(
            q, m, list(perm), duration, load, vehicles_start_times
        )
        # Check if it is the best order
        if vehicle_times is not None and (
            (objective_func_type == "min_max_time" and route_max_time < best_route_max_time)
            or (objective_func_type == "min_sum_time" and route_sum_time < best_route_sum_time)
        ):
            best_route_max_time = route_max_time
            best_route_sum_time = route_sum_time
            best_vehicle_routes = vehicle_routes
            best_vehicle_times = vehicle_times

    if best_vehicle_times is None:
        print("No feasible solution")
    else:
        print(f"Best route max time: {best_route_max_time}")
        print(f"Best route sum time: {best_route_sum_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"Route of vehicle {vehicle_id}: {vehicle_cycles}")
        for vehicle_id, vehicle_time in best_vehicle_times.items():
            print(f"Time of vehicle {vehicle_id}: {vehicle_time}")

    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")

    return best_route_max_time, best_route_sum_time, best_vehicle_routes, best_vehicle_times
