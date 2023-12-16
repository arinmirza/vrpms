import itertools
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple
from src.utilities.utilities2.helper.data_helper import (
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
UNLOADING_DEPOT_TIME_INIT = 30
UNLOADING_DEPOT_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def calculate_duration(
    current_time: float,
    current_location: int,
    perm: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    ignore_long_trip: bool,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the given order of customers

    :param current_time: Current time
    :param current_location: Current (starting) location
    :param perm: Customers to be visited in order
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param ignore_long_trip: Flag to ignore long trips
    :param do_loading_unloading: Spend time to do loading/unloading at the current_location
    :param cancelled_customers: Customers where regarding orders are cancelled
    :return: Total time it takes to visit the locations in the given order and the corresponding route
    """
    route = [current_location] + perm + [DEPOT]
    last_node = current_location

    if do_loading_unloading:
        if current_location != DEPOT:
            current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[current_location]
        else:
            total_load = 0
            for customer in route:
                total_load += load[customer]
            if total_load > 0:
                current_time += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load

    for node in route[1:]:
        hour = int(current_time / TIME_UNITS)
        if not ignore_long_trip:
            hour = min(hour, N_TIME_ZONES - 1)
        if hour >= N_TIME_ZONES:
            return INF, None
        current_time += duration[last_node][node][hour]
        if node != DEPOT:
            current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[node]
        else:
            total_load = 0
            for customer in cancelled_customers:
                total_load += load[customer]
            if total_load > 0:
                current_time += UNLOADING_DEPOT_TIME_INIT + UNLOADING_DEPOT_TIME_PER_UNIT * total_load
        last_node = node

    if ignore_long_trip and current_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, None

    return current_time, route


def solve(
    current_time: float,
    current_location: int,
    customers: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    ignore_long_trip: bool,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param current_time: Current time
    :param current_location: Current (starting) location
    :param customers: Customers to be visited
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param ignore_long_trip: Flag to ignore long trips
    :param do_loading_unloading: ...
    :param cancelled_customers: ...
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < len(duration), "Current location should be in the fetched duration data"
    start_time = datetime.now()
    best_route_time, best_route = INF, None
    for perm in itertools.permutations(customers):
        route_time, route = calculate_duration(
            current_time=current_time,
            current_location=current_location,
            perm=list(perm),
            duration=duration,
            load=load,
            ignore_long_trip=ignore_long_trip,
            do_loading_unloading=do_loading_unloading,
            cancelled_customers=cancelled_customers,
        )
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


def run_request(
    current_time: float,
    current_location: int,
    customers: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    do_loading_unloading: bool,
    cancelled_customers: List[int],
):
    route_time, route = solve(
        duration=duration,
        load=load,
        customers=customers,
        current_time=current_time,
        current_location=current_location,
        do_loading_unloading=do_loading_unloading,
        cancelled_customers=cancelled_customers,
        ignore_long_trip=False,
    )
    result_dict = {"route_time": route_time, "route": route}
    return result_dict


def run(
    n: int = 8,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: float = 5,
    current_time: float = 0,
    current_location: int = DEPOT,
    ignore_long_trip: bool = False,
    do_loading_unloading: bool = True,
    cancelled_customers: List[int] = [],
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Dict:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param n: Number of locations
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param ignore_long_trip: Flag to ignore long trips
    :param duration_data_type: Type of the duration data to be used
    :param do_loading_unloading: Spend time to do loading/unloading at the current_location
    :param cancelled_customers: Customers where regarding orders are cancelled
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, _ = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, n)
    elif duration_data_type == "google":
        duration, _ = get_google_and_load_data(INPUT_FILES_TIME, None, n)
    else:
        duration, _ = get_based_and_load_data(None, n, per_km_time)
    customers = [i for i in range(1, n) if i != current_location]
    load = [0] + [1 for _ in range(1, n)]
    result = solve(
        current_time=current_time,
        current_location=current_location,
        customers=customers,
        duration=duration,
        load=load,
        ignore_long_trip=ignore_long_trip,
        do_loading_unloading=do_loading_unloading,
        cancelled_customers=cancelled_customers,
    )
    result_dict = {"route_time": result[0], "route": result[1]}
    print(f"result_dict = {result_dict}")
    return result_dict


if __name__ == "__main__":
    run()