import itertools
from datetime import datetime
from typing import List, Tuple, Optional
from queue import PriorityQueue
from collections import defaultdict

IGNORE_LONG_TRIP = True

INF = float("inf")
N_TIME_ZONES = 12
DEPOT = 0


def calculate_duration(q: int, m: int, perm: List[int], duration: List[List[List[float]]], load: List[int]) \
        -> Tuple[float, Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations in order and the route

    :param q: The locations to visit in order
    :param m: Max number of vehicles
    :param perm: The locations to visit in order
    :param duration: Dynamic duration data of 12xNxN
    :param load: Loads of locations
    :return: Total time it takes to visit the locations in order and the route
    """
    perm = list(perm)
    perm.append(DEPOT)

    cycles = []
    last_cycle = []
    curr_capacity = q
    for node in perm:
        if node == DEPOT:
            if curr_capacity < 0:
                return INF, None
            else:
                if len(last_cycle) > 0:
                    cycle = [DEPOT]
                    cycle.extend(last_cycle)
                    cycle.append(DEPOT)
                    cycles.append(cycle)
                last_cycle = []
                curr_capacity = q
        else:
            last_cycle.append(node)
            curr_capacity -= load[node]

    vehicle_routes = defaultdict(list)

    vehicles = PriorityQueue()
    for i in range(m):
        vehicles.put((0, i))
    for cycle in cycles:
        vehicle = vehicles.get()
        vehicle_t, vehicle_id = vehicle
        curr_time = vehicle_t
        last_node = DEPOT
        for node in cycle[1:]:
            curr_time_slip = int(curr_time / 60)
            if not IGNORE_LONG_TRIP:
                curr_time_slip = min(curr_time_slip, N_TIME_ZONES-1)
            if curr_time_slip >= N_TIME_ZONES:
                return INF, None
            curr_time += duration[last_node][node][curr_time_slip]
            last_node = node
        vehicles.put((curr_time, vehicle_id))
        vehicle_routes[vehicle_id].append(cycle)

    route_time = 0
    while not vehicles.empty():
        vehicle = vehicles.get()
        vehicle_t, _ = vehicle
        route_time = vehicle_t

    if IGNORE_LONG_TRIP and route_time >= N_TIME_ZONES*60:
        return INF, None

    return route_time, vehicle_routes


def solve(n: int, k: int, q: int, m: int, duration: List[List[List[float]]], load: List[int]) \
        -> Tuple[float, Optional[defaultdict]]:
    """
    Solves VRP using brute force

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param duration: Dynamic duration data
    :param load: Loads of locations
    """
    start_time = datetime.now()
    nodes = [i for i in range(1, n)]
    for _ in range(k-1):
        nodes.append(DEPOT)
    best_route_time, best_vehicle_routes = INF, None
    # Look for each permutation of visiting orders
    for perm in itertools.permutations(nodes):
        route_time, vehicle_routes = calculate_duration(q, m, list(perm), duration, load)
        # Check if it is the best order
        if vehicle_routes is not None and route_time < best_route_time:
            best_route_time = route_time
            best_vehicle_routes = vehicle_routes
    if best_vehicle_routes is None:
        print("No feasible solution")
    else:
        print(f"Best route time: {best_route_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"{vehicle_id}: {vehicle_cycles}")
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")
    return best_route_time, best_vehicle_routes