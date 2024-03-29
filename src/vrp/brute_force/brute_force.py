import copy
import itertools
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple
from src.vrp.vehicles_pq import VehiclesPQ
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)

INF = float("inf")
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60*60 seconds
DEPOT = 0

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]

LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def calculate_duration(
    q: int,
    ignore_long_trip: bool,
    cycles: List[List[int]],
    duration: List[List[List[float]]],
    load: List[int],
    vehicles_start_times: List[float],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given list of cycles

    :param q: Capacity of vehicle
    :param ignore_long_trip: Flag to ignore long trips
    :param cycles: The cycles to be assigned where one cycle is demonstrated as [DEPOT, c_i, ..., c_j, DEPOT]
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    # Initialize vehicle id to cycles and times mapping
    vehicle_routes = defaultdict(list)

    # Initialize the PQ of vehicles (drivers) with given (expected) start time
    vehicles_pq = VehiclesPQ(vehicles_start_times)

    # Cycle: [DEPOT, customer_1, customer_2, ..., customer_k, DEPOT]
    # Cycles: [cycle_1, cycle_2, ...]
    for cycle in cycles:
        # Get the vehicle (driver) with the earliest available time
        vehicle_t, vehicle_id = vehicles_pq.get_vehicle()
        last_node = DEPOT
        curr_capacity = q
        total_load = 0
        for customer in cycle:
            total_load += load[customer]
        if total_load > 0:
            vehicle_t += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load
        # Go over each edge in the cycle
        for node in cycle[1:]:
            # Update capacity and check if it exceeds the initial capacity
            curr_capacity -= load[node]
            if curr_capacity < 0:
                return INF, INF, None, None
            # Determine the hour and check if it exceeds the number of time zones (based on ignore_long_trip)
            hour = int(vehicle_t / TIME_UNITS)
            if not ignore_long_trip:
                hour = min(hour, N_TIME_ZONES - 1)
            if hour >= N_TIME_ZONES:
                return INF, INF, None, None
            # Update time and node
            vehicle_t += duration[last_node][node][hour]
            if node != DEPOT:
                vehicle_t += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[node]
            last_node = node
        # Update PQ with the chosen vehicle and updated time
        vehicles_pq.put_vehicle(vehicle_t, vehicle_id)
        vehicle_routes[vehicle_id].append(cycle)

    # Pull elements from PQ and update vehicle id to cycles and times mapping
    # route_max_time: max of duration among all vehicles (drivers)
    # route_sum_time: sum of duration of all vehicles (drivers)
    route_max_time, route_sum_time, vehicle_times = vehicles_pq.get_route_and_vehicle_times()

    # Check if it exceeds the number of time zones (based on ignore_long_trip)
    if ignore_long_trip and route_max_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, INF, None, None

    return route_max_time, route_sum_time, vehicle_routes, vehicle_times


def calculate_duration_perm(
    q: int,
    ignore_long_trip: bool,
    perm: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    vehicles_start_times: List[float],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given permutation of nodes

    :param q: Capacity of vehicle
    :param ignore_long_trip: Flag to ignore long trips
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
                cycle = [DEPOT] + last_cycle + [DEPOT]
                cycles.append(cycle)
                last_cycle = []
        else:
            last_cycle.append(node)

    return calculate_duration(q, ignore_long_trip, cycles, duration, load, vehicles_start_times)


def solve(
    k: int,
    q: int,
    ignore_long_trip: bool,
    duration: List[List[List[float]]],
    load: List[int],
    customers: List[int],
    vehicles_start_times: Optional[List[float]],
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_max_time",
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Solves VRP using brute force and gets total time it takes to visit the locations for the latest driver, sum of the
        durations of each driver and the routes for each driver

    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param ignore_long_trip: Flag to ignore long trips
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param customers: List of customers to be visited
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :return: Among the all possible routes, total time it takes to visit the locations for the latest driver, sum of the
        durations of each driver, the routes for each driver and the travel duration for each driver
    """
    start_time = datetime.now()

    (
        best_route_max_time,
        best_route_sum_time,
        best_vehicle_routes,
        best_vehicle_times,
    ) = (INF, INF, None, None)

    nodes = copy.deepcopy(customers)
    nodes.extend([DEPOT for _ in range(1, k)])

    # Look for each permutation of visiting orders
    for perm in itertools.permutations(nodes):
        (
            route_max_time,
            route_sum_time,
            vehicle_routes,
            vehicle_times,
        ) = calculate_duration_perm(q, ignore_long_trip, list(perm), duration, load, vehicles_start_times)
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

    return (
        best_route_max_time,
        best_route_sum_time,
        best_vehicle_routes,
        best_vehicle_times,
    )


def run_request(
    q: int,
    duration: List[List[List[float]]],
    load: List[int],
    available_customers: List[int],
    vehicles_start_times: Optional[List[float]],
    ignore_long_trip: bool = False,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_max_time",
) -> Dict:
    sum_demand = 0
    for customer in available_customers:
        sum_demand += load[customer]
    k = (sum_demand + q - 1) // q
    result = solve(
        k=k,
        q=q,
        ignore_long_trip=ignore_long_trip,
        duration=duration,
        load=load,
        customers=available_customers,
        vehicles_start_times=vehicles_start_times,
        objective_func_type=objective_func_type,
    )
    result_dict = {
        "route_max_time": result[0],
        "route_sum_time": result[1],
        "vehicles_routes": result[2],
        "vehicles_times": result[3],
    }
    return result_dict


def run(
    n: int = 8,
    m: int = 5,
    k: int = 3,
    q: int = 5,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: float = 5,
    ignore_long_trip: bool = False,
    input_file_load: Optional[str] = None,
    vehicles_start_times: Optional[List[float]] = None,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_sum_time",
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Dict:
    """
    Gets dynamic time data of the common dataset and solves VRP using brute force

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param ignore_long_trip: Flag to ignore long trips
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique. Example: "../../../data/loads/data_load.txt"
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :param duration_data_type: Type of the duration data to be used
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    objective_func_type = objective_func_type.lower()
    assert objective_func_type in [
        "min_max_time",
        "min_sum_time",
    ], f"{objective_func_type} as a function type is not implemented"

    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"

    if vehicles_start_times is None:
        vehicles_start_times = [0 for _ in range(m)]
    else:
        assert len(vehicles_start_times) == m, f"Size of the vehicles_start_times should be {m}"

    if duration_data_type == "mapbox":
        duration, load = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, n)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)

    customers = [i for i in range(1, n)]

    result = solve(
        k=k,
        q=q,
        ignore_long_trip=ignore_long_trip,
        duration=duration,
        load=load,
        customers=customers,
        vehicles_start_times=vehicles_start_times,
        objective_func_type=objective_func_type,
    )
    result_dict = {
        "route_max_time": result[0],
        "route_sum_time": result[1],
        "vehicles_routes": result[2],
        "vehicles_times": result[3],
    }
    print(f"result_dict = {result_dict}")
    return result_dict


if __name__ == "__main__":
    run()
