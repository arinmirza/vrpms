from collections import defaultdict
from typing import List, Tuple, Union

from src.utilities.helper.tsp_helper import route_solution_to_arrivals


def vehicle_solution_to_arrivals(
    vehicle_start_time: float,
    vehicle_solution: List[List[int]],
    duration: List[List[List[float]]],
    load: List[int],
) -> Tuple[List[Tuple[List[float], float]], float]:
    """
    Gets arrival times for each node given in the solution

    :param vehicle_start_time: Start times of the vehicle
    :param vehicle_solution: Tour of the driver
    :param duration: Dynamic duration data
    :param load: Loads of locations
    :return: Arrival times for each node given in the solution
    """
    current_time = vehicle_start_time
    arrivals_vehicle = []
    for route in vehicle_solution:
        arrivals_cycle, current_time = route_solution_to_arrivals(
            vehicle_start_time=current_time,
            route=route,
            duration=duration,
            load=load,
            do_loading_unloading=True,
            cancelled_customers=[],
        )
        arrivals_vehicle.append((arrivals_cycle, current_time))
    return arrivals_vehicle, current_time


def complete_solution_to_arrivals(
    vehicles_start_times: List[float],
    solution: List[List[List[int]]],
    duration: List[List[List[float]]],
    load: List[int],
) -> Tuple[List[Tuple[List[Tuple[List[float], float]], float]], defaultdict, float, float]:
    """
    Gets arrival times for each node given in the solution

    :param vehicles_start_times: List of start times of vehicles
    :param solution: Tours for each drivers
    :param duration: Dynamic duration data
    :param load: Loads of locations
    :return: Arrival times for each node given in the solution
    """
    m = len(vehicles_start_times)
    arrivals = []
    route_max_time, route_sum_time = 0, 0
    vehicle_times = defaultdict(float)
    for vehicle_id in range(m):
        vehicle_start_time = vehicles_start_times[vehicle_id]
        vehicle_solution = solution[vehicle_id]
        arrivals_vehicle, vehicle_t = vehicle_solution_to_arrivals(vehicle_start_time, vehicle_solution, duration, load)
        arrivals.append((arrivals_vehicle, vehicle_t))
        vehicle_times[vehicle_id] = vehicle_t
        route_sum_time += vehicle_t
        route_max_time = max(route_max_time, vehicle_t)
    return arrivals, vehicle_times, route_max_time, route_sum_time
