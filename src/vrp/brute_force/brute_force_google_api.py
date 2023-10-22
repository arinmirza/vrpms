from collections import defaultdict
from typing import List, Literal, Optional, Tuple

from src.vrp.brute_force.brute_force import solve
from src.utilities.vrp_helper import get_google_and_load_data

N_TIME_ZONES = 12
INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def run(
    n: int = 8,
    m: int = 2,
    k: int = 3,
    q: int = 3,
    ignore_long_trip: bool = False,
    input_file_load: Optional[str] = None,
    ignored_customers: Optional[List[int]] = None,
    vehicles_start_times: Optional[List[float]] = None,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_sum_time",
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Gets dynamic time data of Google Maps dataset and solves VRP using brute force

    :param n: Number of locations
    :param m: Max number of vehicles
    :param k: Max number of cycles
    :param q: Capacity of vehicle
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
    duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
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
