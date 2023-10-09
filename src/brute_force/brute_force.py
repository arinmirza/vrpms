import itertools
from datetime import datetime
from typing import List, Tuple, Optional
from queue import PriorityQueue
from collections import defaultdict

IGNORE_LONG_TRIP = True

INF = float("inf")
N_TIME_ZONES = 12
DEPOT = 0


def calculate_duration(q: int, m: int, cycles: List[List[int]], duration: List[List[List[float]]], load: List[int]) -> \
        Tuple[float, float, Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given list of cycles

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param cycles: The cycles to be assigned where one cycle is demonstrated as [DEPOT, c_i, ..., c_j, DEPOT]
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver
    """
    vehicle_routes = defaultdict(list)

    vehicles = PriorityQueue()
    for i in range(m):
        vehicles.put((0, i))
    for cycle in cycles:
        vehicle = vehicles.get()
        vehicle_t, vehicle_id = vehicle
        curr_time = vehicle_t
        last_node = DEPOT
        curr_capacity = q
        for node in cycle[1:]:
            curr_capacity -= load[node]
            if curr_capacity < 0:
                return INF, INF, None
            curr_time_slip = int(curr_time / 60)
            if not IGNORE_LONG_TRIP:
                curr_time_slip = min(curr_time_slip, N_TIME_ZONES-1)
            if curr_time_slip >= N_TIME_ZONES:
                return INF, INF, None
            curr_time += duration[last_node][node][curr_time_slip]
            last_node = node
        vehicles.put((curr_time, vehicle_id))
        vehicle_routes[vehicle_id].append(cycle)

    route_max_time = 0
    route_sum_time = 0
    while not vehicles.empty():
        vehicle = vehicles.get()
        vehicle_t, _ = vehicle
        route_max_time = vehicle_t
        route_sum_time += vehicle_t

    if IGNORE_LONG_TRIP and route_max_time >= N_TIME_ZONES*60:
        return INF, INF, None

    return route_max_time, route_sum_time, vehicle_routes


def calculate_duration_perm(q: int, m: int, perm: List[int], duration: List[List[List[float]]], load: List[int]) \
        -> Tuple[float, float, Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given permutation of nodes

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param perm: The locations to visit in order
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver
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

    return calculate_duration(q, m, cycles, duration, load)


def solve(n: int, k: int, q: int, m: int, duration: List[List[List[float]]], load: List[int]) \
        -> Tuple[float, float, Optional[defaultdict]]:
    """
    Solves VRP using brute force and gets total time it takes to visit the locations for the latest driver, sum of the
        durations of each driver and the routes for each driver

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver
    """
    start_time = datetime.now()
    nodes = [i for i in range(1, n)]
    for _ in range(k-1):
        nodes.append(DEPOT)
    best_route_max_time, best_route_sum_time, best_vehicle_routes = INF, INF, None
    # Look for each permutation of visiting orders
    for perm in itertools.permutations(nodes):
        route_max_time, route_sum_time, vehicle_routes = calculate_duration_perm(q, m, list(perm), duration, load)
        # Check if it is the best order
        if vehicle_routes is not None and route_max_time < best_route_max_time:
            best_route_max_time = route_max_time
            best_route_sum_time = route_sum_time
            best_vehicle_routes = vehicle_routes
    if best_vehicle_routes is None:
        print("No feasible solution")
    else:
        print(f"Best route max time: {best_route_max_time}")
        print(f"Best route sum time: {best_route_sum_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"{vehicle_id}: {vehicle_cycles}")
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")
    return best_route_max_time, best_route_sum_time, best_vehicle_routes
