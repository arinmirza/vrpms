from collections import defaultdict
from typing import List, Literal, Optional, Tuple

from src.vrp.brute_force.brute_force import solve
from src.utilities.helper.data_helper import get_mapbox_and_local_data


def run(
    n: int = 8,
    m: int = 2,
    k: int = 3,
    q: int = 5,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    ignore_long_trip: bool = False,
    input_file_load: Optional[str] = None,
    ignored_customers: Optional[List[int]] = None,
    vehicles_start_times: Optional[List[float]] = None,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_sum_time",
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Gets dynamic time data of the common dataset and solves VRP using brute force

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param ignore_long_trip: Flag to ignore long trips
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique. Example: "../../../data/loads/data_load.txt"
    :param ignored_customers: List of customers to be ignored by the algorithm
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    duration, load = get_mapbox_and_local_data(supabase_url, supabase_key, supabase_url_key_file, input_file_load, n)
    return solve(
        n=n,
        m=m,
        k=k,
        q=q,
        ignore_long_trip=ignore_long_trip,
        duration=duration,
        load=load,
        ignored_customers=ignored_customers,
        vehicles_start_times=vehicles_start_times,
        objective_func_type=objective_func_type,
    )


if __name__ == "__main__":
    run()
