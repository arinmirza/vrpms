from collections import defaultdict
from typing import Dict, List, Literal, Optional, Tuple

from api.database import Database
from src.utilities.helper.vrp_helper import vehicle_solution_to_arrivals
from src.utilities.helper.data_helper import get_based_and_load_data, get_google_and_load_data
from src.vrp.ant_colony.aco_hybrid import solve as solve_aco_vrp
from src.tsp.ant_colony.aco_hybrid import solve as solve_aco_tsp
from src.utilities.helper.locations_helper import convert_locations, get_demands_from_locations

DEPOT = 0  # depot
N_TIME_ZONES = 12  # hours = time slices
EPS = 1e-6
INF = float("inf")

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def remove_customers_to_be_delayed_and_cancelled(
    vehicle_id: int,
    customers: List[int],
    delay_customers: List[int],
    cancel_customers: List[int],
    cycle: List[int],
) -> None:
    customers_to_be_delayed = list(set(cycle) & set(delay_customers))
    for customer in customers_to_be_delayed:
        print(f"Customer {customer} is delayed for the driver {vehicle_id}")
        cycle.remove(customer)
        delay_customers.remove(customer)
    customers_to_be_cancelled = list(set(cycle) & set(cancel_customers))
    for customer in customers_to_be_cancelled:
        print(f"Customer {customer} is cancelled for the driver {vehicle_id}")
        cycle.remove(customer)
        cancel_customers.remove(customer)
        customers.remove(customer)


def run_tsp_algo(
    n: int,
    customers: List[int],
    duration: List[List[List[float]]],
    vehicle_start_time: float,
    vehicle_start_node: int,
    tsp_algo_params: Dict,
) -> List[int]:
    algo = tsp_algo_params["algo"]
    tsp_sol = None
    if algo == "bf":
        ...
    elif algo == "aco":
        tsp_sol = solve_aco_tsp(
            n=n,
            duration=duration,
            customers=customers,
            current_time=vehicle_start_time,
            current_location=vehicle_start_node,
            n_hyperparams=tsp_algo_params["n_hyperparams"],
            n_best_results=1,
            is_print_allowed=False,
        )
        tsp_sol = tsp_sol[0][1]
    elif algo == "sa":
        ...
    elif algo == "ga":
        ...
    else:
        raise "Algo not defined"
    return tsp_sol


def tsp_optimize(
    n: int,
    tsp_freq: int,
    vehicle_id: int,
    vehicle_start_time: float,
    init_cycle: List[int],
    duration: List[List[List[float]]],
    tsp_algo_params: Dict,
) -> List[int]:
    if tsp_freq <= 0:
        return init_cycle
    init_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [init_cycle], duration)
    init_vehicle_finish_time = init_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} before TSP optimization")
    print(f"Route time: {init_vehicle_finish_time}")
    print(f"Route: {init_cycle}")
    print()
    n_cycle_nodes = len(init_cycle)
    final_cycle = init_cycle.copy()
    for i in range(0, n_cycle_nodes - 3, tsp_freq):
        customers = final_cycle[i + 1 : -1]
        curr_vehicle_start_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle[: i + 1]], duration)
        curr_vehicle_start_time = curr_vehicle_start_times[0][-1]
        print(f"customers={customers} , final_cycle={final_cycle} , i={i}")
        tsp_sol = run_tsp_algo(
            n=n,
            customers=customers,
            duration=duration,
            vehicle_start_time=curr_vehicle_start_time,
            vehicle_start_node=final_cycle[i],
            tsp_algo_params=tsp_algo_params,
        )
        print(f"tsp_sol = {tsp_sol}")
        final_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle], duration)
        final_vehicle_finish_time = final_vehicle_finish_times[0][-1]
        new_vehicle_finish_times = vehicle_solution_to_arrivals(curr_vehicle_start_time, [tsp_sol], duration)
        new_vehicle_finish_time = new_vehicle_finish_times[0][-1]
        improved = new_vehicle_finish_time < final_vehicle_finish_time
        if improved:
            print(f"Partial TSP improvement")
            print(f"Route time: from {final_vehicle_finish_time} to {new_vehicle_finish_time}")
            print(f"Route: from {final_cycle[i:]} to {tsp_sol}")
            final_cycle[i:] = tsp_sol
    final_vehicle_finish_times = vehicle_solution_to_arrivals(vehicle_start_time, [final_cycle], duration)
    final_vehicle_finish_time = final_vehicle_finish_times[0][-1]
    print(f"Vehicle {vehicle_id} after TSP optimization")
    print(f"Route time: {final_vehicle_finish_time}")
    print(f"Route: {final_cycle}")
    improved = final_vehicle_finish_time < init_vehicle_finish_time
    print("TSP improvement" if improved else "No improvement")
    print()
    return final_cycle if improved else init_cycle


def run_vrp_algo(
    n: int,
    m: int,
    k: int,
    q: int,
    customers: List[int],
    duration: List[List[List[float]]],
    demands: Optional[List[int]],
    vehicles_start_times: List[float],
    vrp_algo_params: Dict,
):
    algo = vrp_algo_params["algo"]
    vrp_sol = None
    if algo == "bf":
        ...
    elif algo == "aco":
        vrp_sol = solve_aco_vrp(
            n=n,
            m=m,
            k=k,
            q=q,
            duration=duration,
            customers=customers,
            load=demands,
            vehicles_start_times=vehicles_start_times,
            n_hyperparams=vrp_algo_params["n_hyperparams"],
            n_best_results=1,
            is_print_allowed=False,
        )
        vrp_sol = vrp_sol[0][2]
    elif algo == "sa":
        ...
    elif algo == "ga":
        ...
    else:
        raise "Algo not defined"
    return vrp_sol


def solve_scenario(
    n: int,
    m: int,
    k: int,
    q: int,
    tsp_freq: int,
    customers: List[int],
    delay_customers: List[int],
    cancel_customers: List[int],
    duration: List[List[List[float]]],
    demands: Optional[List[int]],
    vrp_algo_params: Dict,
    tsp_algo_params: Dict,
) -> Tuple[defaultdict, List[float]]:
    vehicles_start_times = [0 for _ in range(m)]
    vehicle_routes = defaultdict(list)
    while len(customers) > 0:
        total_demands = 0
        for customer in customers:
            total_demands += demands[customer]
        k_min = (total_demands + q - 1) // q
        k = max(k, k_min)
        min_vehicle_start_times = min(vehicles_start_times)
        available_vehicles = [i for i in range(m) if abs(vehicles_start_times[i] - min_vehicle_start_times) < EPS]
        vrp_sol = run_vrp_algo(
            n=n,
            m=m,
            k=k,
            q=q,
            customers=customers,
            duration=duration,
            demands=demands,
            vehicles_start_times=vehicles_start_times,
            vrp_algo_params=vrp_algo_params,
        )
        print(f"vehicle_routes: {vehicle_routes}")
        print(f"vehicles_start_times: {vehicles_start_times}")
        print(f"customers: {customers}")
        print(f"vrp_sol: {vrp_sol}")
        print("")
        for vehicle_id in available_vehicles:
            if len(vrp_sol[vehicle_id]) > 0:
                cycle = vrp_sol[vehicle_id][0]
                remove_customers_to_be_delayed_and_cancelled(
                    vehicle_id, customers, delay_customers, cancel_customers, cycle
                )
                if cycle == [DEPOT, DEPOT]:
                    continue
                vehicle_start_time = min_vehicle_start_times  # vehicles_start_times[vehicle_id]
                cycle = tsp_optimize(
                    n=n,
                    tsp_freq=tsp_freq,
                    vehicle_id=vehicle_id,
                    vehicle_start_time=vehicle_start_time,
                    init_cycle=cycle,
                    duration=duration,
                    tsp_algo_params=tsp_algo_params,
                )
                k -= 1
                vehicle_routes[vehicle_id].append(cycle)
                vehicle_arrivals = vehicle_solution_to_arrivals(vehicle_start_time, [cycle], duration)
                vehicles_start_times[vehicle_id] = vehicle_arrivals[0][-1]
                for customer in cycle[1:-1]:
                    customers.remove(customer)
    print("FINAL")
    print(f"vehicle_routes: {vehicle_routes}")
    print(f"vehicles_finish_times: {vehicles_start_times}")
    print(f"customers: {customers}")
    return vehicle_routes, vehicles_start_times


def run(
    n: int = 21,
    m: int = 3,
    k: int = 4,
    q: int = 6,
    tsp_freq: int = 2,
    ignore_customers: List[int] = [1],
    delay_customers: List[int] = [2],
    cancel_customers: List[int] = [3],
    durations_query_row_id: int = 1,
    locations_query_row_id: int = 2,
    per_km_time: int = 1,
    input_file_load: Optional[str] = None,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
    vrp_algo_params: Dict = {"algo": "aco", "n_hyperparams": 10},
    tsp_algo_params: Dict = {"algo": "aco", "n_hyperparams": 10},
) -> Tuple[defaultdict, List[float]]:
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    if duration_data_type == "mapbox":
        errors = []
        database = Database()
        duration = database.get_durations_by_id(durations_query_row_id, errors)
        locations = database.get_locations_by_id(locations_query_row_id, errors)
        new_locations = convert_locations(locations)
        load = get_demands_from_locations(duration, new_locations)
    elif duration_data_type == "google":
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    customers = [i for i in range(1, n) if i not in ignore_customers]
    vehicle_routes, vehicles_finish_times = solve_scenario(
        n=n,
        m=m,
        k=k,
        q=q,
        tsp_freq=tsp_freq,
        customers=customers,
        delay_customers=delay_customers,
        cancel_customers=cancel_customers,
        duration=duration,
        demands=load,
        vrp_algo_params=vrp_algo_params,
        tsp_algo_params=tsp_algo_params,
    )
    return vehicle_routes, vehicles_finish_times


if __name__ == "__main__":
    run()
