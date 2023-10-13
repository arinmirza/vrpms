from collections import defaultdict
from typing import List, Optional, Tuple

from src.brute_force.brute_force import solve
from src.utilities.vrp_helper import get_based_and_load_data


# input_file_load: "../../../data/loads/data_load.txt"
def run(
    n: int = 8,
    k: int = 3,
    q: int = 5,
    m: int = 2,
    per_km_time: float = 5,
    input_file_load: Optional[str] = None,
    ignored_customers: Optional[List[int]] = None,
) -> Tuple[float, float, Optional[defaultdict]]:
    """
    Gets dynamic time data of the common dataset and solves VRP using brute force

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param ignored_customers: List of customers to be ignored by the algorithm
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver
    """
    duration, load = get_based_and_load_data(input_file_load, n, per_km_time, True)
    return solve(n, k, q, m, duration, load, ignored_customers)


if __name__ == "__main__":
    run()
