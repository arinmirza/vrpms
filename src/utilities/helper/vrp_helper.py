from typing import List

DEPOT = 0
TIME_UNITS = 60  # hour = 60 minutes


def solution_to_arrivals(
    vehicles_start_times: List[float],
    solution: List[List[List[int]]],
    duration: List[List[List[float]]],
) -> List[List[List[float]]]:
    """
    Gets arrival times for each node given in the solution

    :param vehicles_start_times: List of start times of vehicles
    :param solution: Tours for each drivers
    :param duration: Dynamic duration data
    :return: Arrival times for each node given in the solution
    """
    assert len(vehicles_start_times) == len(solution), "Size of the vehicle start time and solution do not match"
    arrivals = []
    for vehicle_id, vehicle_start_time in enumerate(vehicles_start_times):
        current_node = DEPOT
        current_time = vehicle_start_time
        arrivals_vehicle = []
        for cycle in solution[vehicle_id]:
            arrivals_vehicle_cycle = []
            for node in cycle:
                hour = int(current_time / TIME_UNITS)
                current_time += duration[current_node][node][hour]
                arrivals_vehicle_cycle.append(current_time)
                current_node = node
            arrivals_vehicle.append(arrivals_vehicle_cycle)
        arrivals.append(arrivals_vehicle)
    return arrivals
