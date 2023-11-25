import json
from collections import defaultdict
from typing import Dict, List, Tuple

from api.database import DatabaseVRP
from src.scenarios.aco_serve_all import solve_scenario
from src.utilities.helper.locations_helper import (
    convert_locations,
    get_demands_from_locations,
    remove_unused_locations_vrp,
)
from src.utilities.helper.result_2_output import vrp_result_2_output

ACCESS_TOKEN = ""
RECORD_NAME = "simulation_scenario_name"
RECORD_DESCRIPTION = "simulation_scenario_description"


def upload_supabase(
    n: int,
    m: int,
    q: int,
    vehicles_routes: defaultdict,
    duration: List[List[List[float]]],
    locations: List[Dict],
    ignore_customers: List[int],
) -> Dict:
    """
    Uploads the result of simulation to a new Supabase row

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param m: The number of vehicles
    :param q: The capacity of vehicles
    :param vehicles_routes: List of location ids to visit where first and last element of each 1D inner list (cycle) is
        DEPOT
    :param duration: Duration data of NxNx12
    :param locations: Locations already stored in a Supabase record
    :param ignore_customers: Customers to ignore orders
    :return: Record (json) to be stored in Supabase
    """
    new_locations = convert_locations(locations)
    filtered_locations = remove_unused_locations_vrp(locations, ignore_customers, [], n)
    vehicles_start_times = [0 for _ in range(m)]
    capacities = [q for _ in range(m)]
    vrp_result = {"vehicles_routes": vehicles_routes}
    result = vrp_result_2_output(
        vehicles_start_times=vehicles_start_times,
        duration=duration,
        locations=new_locations,
        vrp_result=vrp_result,
        capacities=capacities,
    )
    errors = []
    database = DatabaseVRP(ACCESS_TOKEN)
    duration_max = int(result["durationMax"])
    duration_sum = int(result["durationSum"])
    database.save_solution(
        name=RECORD_NAME,
        description=RECORD_DESCRIPTION,
        locations=filtered_locations,
        vehicles=result["vehicles"],
        duration_max=duration_max,
        duration_sum=duration_sum,
        errors=errors,
    )
    print(f"\n{result}")
    return result


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
    vrp_algo_params_path: str = "../../data/scenarios/vrp/config_vrp_aco_1.json",
    tsp_algo_params_path: str = "../../data/scenarios/tsp/config_tsp_bf_1.json",
) -> Dict:
    """
    Runs the given scenario and simulate the entire day with a couple of VRPs and TSP optimizations for each VRP

    :param n: The number of locations, it should be larger than id of the depot and the given customers
    :param m: The number of vehicles
    :param k: The number of max cycles
    :param q: The capacity of vehicles
    :param tsp_freq: Frequency of the TSP to run in terms of the number of locations
    :param ignore_customers: Customers to ignore orders
    :param delay_customers: Customers to delay orders
    :param cancel_customers: Customers to cancel orders
    :param durations_query_row_id: Row ID of the "durations" table to be fetched
    :param locations_query_row_id: Row ID of the "locations" table to be fetched
    :param vrp_algo_params_path: Path to the file of params to run VRP algo, it should include "algo" as a key
    :param tsp_algo_params_path: Path to the file of params to run TSP algo, it should include "algo" as a key
    :return: List of location ids to visit where first and last element of each 1D inner list (cycle) is DEPOT and list
        of vehicle finish times in terms of seconds
    """
    errors = []
    database = DatabaseVRP()
    duration = database.get_durations_by_id(durations_query_row_id, errors)
    locations = database.get_locations_by_id(locations_query_row_id, errors)
    new_locations = convert_locations(locations)
    load = get_demands_from_locations(duration, new_locations)
    customers = [i for i in range(1, n) if i not in ignore_customers]
    vehicles_routes, _ = solve_scenario(
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
        vrp_algo_params_path=vrp_algo_params_path,
        tsp_algo_params_path=tsp_algo_params_path,
    )
    record = upload_supabase(n, m, q, vehicles_routes, duration, locations, ignore_customers)
    return record


if __name__ == "__main__":
    run()
