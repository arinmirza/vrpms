from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from src.utilities.helper.vrp_helper import solution_to_arrivals
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_local_data,
)
from src.vrp.ant_colony.aco_hybrid import solve as solve_aco

DEPOT = 0
N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6
INF = float("inf")

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def solve_scenario(
    n: int,
    m: int,
    k: int,
    q: int,
    duration: List[List[List[float]]],
    load: Optional[List[int]],
) -> defaultdict:
    vehicles_start_times = [0 for _ in range(m)]
    ignored_customers = []
    vehicle_routes = defaultdict(list)
    while len(ignored_customers) < n - 1:
        min_vehicle_start_times = min(vehicles_start_times)
        available_vehicles = [i for i in range(m) if abs(vehicles_start_times[i] - min_vehicle_start_times) < EPS]
        vrp_sol = solve_aco(
            n=n,
            m=m,
            k=k,
            q=q,
            duration=duration,
            load=load,
            n_hyperparams=10,
            n_best_results=1,
            ignored_customers=ignored_customers,
            vehicles_start_times=vehicles_start_times,
            is_print_allowed=False,
        )
        vrp_sol = vrp_sol[0][2]
        solution_routes = []
        for vehicle_id in range(m):
            solution_routes.append(vrp_sol[vehicle_id])
        print(f"vehicle_routes: {vehicle_routes}")
        print(f"vehicles_start_times: {vehicles_start_times}")
        print(f"ignored_customers: {ignored_customers}")
        print(f"vrp_sol: {vrp_sol}")
        print("")
        arrivals = solution_to_arrivals(vehicles_start_times, solution_routes, duration)
        for vehicle_id in available_vehicles:
            if len(arrivals[vehicle_id]) > 0:
                cycle = vrp_sol[vehicle_id][0]
                vehicle_routes[vehicle_id].append(cycle)
                vehicles_start_times[vehicle_id] = arrivals[vehicle_id][0][-1]
                for node in cycle:
                    if node != DEPOT:
                        ignored_customers.append(node)
    print(f"vehicle_routes: {vehicle_routes}")
    print(f"vehicles_start_times: {vehicles_start_times}")
    print(f"ignored_customers: {ignored_customers}")
    return vehicle_routes


def run(
    n: int = 10,
    m: int = 2,
    k: int = 10,
    q: int = 3,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: str = "mapbox",
) -> defaultdict:
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, load = get_mapbox_and_local_data(
            supabase_url, supabase_key, supabase_url_key_file, input_file_load, n
        )
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    result = solve_scenario(n=n, m=m, k=k, q=q, duration=duration, load=load)
    return result


if __name__ == "__main__":
    run()
