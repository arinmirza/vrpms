from collections import defaultdict
from typing import List, Literal, Optional

from src.utilities.helper.vrp_helper import vehicle_solution_to_arrivals
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_load_data,
)
from src.vrp.ant_colony.aco_hybrid import solve as solve_aco_vrp
from src.tsp.ant_colony.aco_hybrid import solve as solve_aco_tsp

DEPOT = 0
N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6
INF = float("inf")

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def remove_customers_to_be_delayed(vehicle_id: int, cycle: List[int], delay_customers: List[int]) -> None:
    customers_to_be_delayed = list(set(cycle) & set(delay_customers))
    for customer in customers_to_be_delayed:
        print(f"Costumer {customer} is delayed for the driver {vehicle_id}")
        cycle.remove(customer)
        delay_customers.remove(customer)


def tsp_optimize(
    n: int,
    tsp_freq: int,
    vehicle_id: int,
    vehicle_start_time: float,
    cycle: List[int],
    duration: List[List[List[float]]],
) -> List[int]:
    if tsp_freq <= 0:
        return cycle
    old_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [cycle], duration)
    old_vehicle_finish_time = old_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} before TSP optimization")
    print(f"Route time: {old_vehicle_finish_time}")
    print(f"Route: {cycle}")
    print()
    n_cycle_nodes = len(cycle)
    new_cycle = cycle.copy()
    for i in range(0, n_cycle_nodes - 3, tsp_freq):
        customers = new_cycle[i + 1 : -1]
        new_vehicle_start_times = vehicle_solution_to_arrivals(vehicle_start_time, [new_cycle[: i + 1]], duration)
        new_vehicle_start_time = new_vehicle_start_times[0][-1]
        tsp_sol = solve_aco_tsp(
            n=n,
            duration=duration,
            customers=customers,
            current_time=new_vehicle_start_time,
            current_location=new_cycle[i],
            is_print_allowed=False,
        )
        tsp_sol_cycle = tsp_sol[0][1]
        new_cycle[i:] = tsp_sol_cycle
    new_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [new_cycle], duration)
    new_vehicle_finish_time = new_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} after TSP optimization")
    print(f"Route time: {new_vehicle_finish_time}")
    print(f"Route: {new_cycle}")
    print("Improved" if new_vehicle_finish_time < old_vehicle_finish_time else "No improvement")
    print()
    return new_cycle if new_vehicle_finish_time < old_vehicle_finish_time else cycle


def solve_scenario(
    n: int,
    m: int,
    k: int,
    q: int,
    tsp_freq: int,
    delay_customers: List[int],
    duration: List[List[List[float]]],
    load: Optional[List[int]],
) -> defaultdict:
    vehicles_start_times = [0 for _ in range(m)]
    ignored_customers = []
    vehicle_routes = defaultdict(list)
    while len(ignored_customers) < n - 1:
        min_vehicle_start_times = min(vehicles_start_times)
        available_vehicles = [i for i in range(m) if abs(vehicles_start_times[i] - min_vehicle_start_times) < EPS]
        vrp_sol = solve_aco_vrp(
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
        for vehicle_id in available_vehicles:
            if len(vrp_sol[vehicle_id]) > 0:
                cycle = vrp_sol[vehicle_id][0]
                remove_customers_to_be_delayed(vehicle_id, cycle, delay_customers)
                vehicle_start_time = vehicles_start_times[vehicle_id]
                cycle = tsp_optimize(n, tsp_freq, vehicle_id, vehicle_start_time, cycle, duration)
                vehicle_routes[vehicle_id].append(cycle)
                vehicle_arrivals = vehicle_solution_to_arrivals(vehicle_start_time, [cycle], duration)
                vehicles_start_times[vehicle_id] = vehicle_arrivals[0][-1]
                new_ignored_customers = [node for node in cycle if node != DEPOT]
                ignored_customers.extend(new_ignored_customers)
    print("FINAL")
    print(f"vehicle_routes: {vehicle_routes}")
    print(f"vehicles_finish_times: {vehicles_start_times}")
    print(f"ignored_customers: {ignored_customers}")
    return vehicle_routes


def run(
    n: int = 21,
    m: int = 2,
    k: int = 10,
    q: int = 5,
    tsp_freq: int = 2,
    delay_customers: List[int] = [1, 3],
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> defaultdict:
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        duration, load = get_mapbox_and_load_data(supabase_url, supabase_key, supabase_url_key_file, n)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    result = solve_scenario(
        n=n, m=m, k=k, q=q, tsp_freq=tsp_freq, delay_customers=delay_customers, duration=duration, load=load
    )
    return result


if __name__ == "__main__":
    run()
