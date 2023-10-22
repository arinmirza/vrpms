from typing import List, Optional, Tuple

from src.tsp.brute_force.brute_force import solve
from src.utilities.vrp_helper import get_google_and_load_data

DEPOT = 0
N_TIME_ZONES = 12
INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def run(
    n: int = 8,
    current_time: float = 0,
    current_location: int = DEPOT,
    ignore_long_trip: bool = False,
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param n: Number of locations
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param ignore_long_trip: Flag to ignore long trips
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    duration, _ = get_google_and_load_data(INPUT_FILES_TIME, None, n)
    customers = [i for i in range(1, n) if i != current_location]
    return solve(current_time, current_location, customers, duration, ignore_long_trip)


if __name__ == "__main__":
    run()
