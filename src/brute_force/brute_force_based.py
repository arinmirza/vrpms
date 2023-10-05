from src.brute_force.brute_force import solve
from src.utilities.vrp_helper import get_based_and_load_data
from typing import Tuple, Optional
from collections import defaultdict


# input_file_load: "../../../data/loads/data_load.txt"
def run(n: int = 8, k: int = 3, q: int = 5, m: int = 2, per_km_time: float = 5, input_file_load: Optional[str] = None) \
        -> Tuple[float, Optional[defaultdict]]:
    """
    Gets dynamic time data of the common dataset and solves VRP using brute force

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    """
    duration, load = get_based_and_load_data(input_file_load, n, per_km_time, True)
    return solve(n, k, q, m, duration, load)


if __name__ == '__main__':
    run()
