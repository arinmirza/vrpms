from typing import List, Tuple

from src.utilities.helper.tsp_helper import route_solution_to_arrivals


def vehicle_solution_to_arrivals(
    vehicle_start_time: float,
    vehicle_solution: List[List[int]],
    duration: List[List[List[float]]],
    load: List[int],
) -> List[Tuple[List[float], float]]:
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
    return arrivals_vehicle


def solution_to_arrivals(
    vehicles_start_times: List[float],
    solution: List[List[List[int]]],
    duration: List[List[List[float]]],
    load: List[int],
) -> List[List[Tuple[List[float], float]]]:
    """
    Gets arrival times for each node given in the solution

    :param vehicles_start_times: List of start times of vehicles
    :param solution: Tours for each drivers
    :param duration: Dynamic duration data
    :param load: Loads of locations
    :return: Arrival times for each node given in the solution
    """
    assert len(vehicles_start_times) == len(solution), "Size of the vehicle start time and solution do not match"
    arrivals = []
    for vehicle_start_time, vehicle_solution in zip(vehicles_start_times, solution):
        arrivals_vehicle = vehicle_solution_to_arrivals(vehicle_start_time, vehicle_solution, duration, load)
        arrivals.append(arrivals_vehicle)
    return arrivals
