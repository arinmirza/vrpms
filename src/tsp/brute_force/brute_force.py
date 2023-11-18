import itertools
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple
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


def run(
    n: int = 8,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: float = 5,
    current_time: float = 0,
    current_location: int = DEPOT,
    ignore_long_trip: bool = False,
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
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, load = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, None, n)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, None, n)
    else:
        duration, load = get_based_and_load_data(None, n, per_km_time)
    customers = [i for i in range(1, n) if i != current_location]
    result = solve(current_time, current_location, customers, duration, ignore_long_trip)
    result_dict = {"route_time": result[0], "route": result[1]}
    return result_dict


if __name__ == "__main__":
    run()
