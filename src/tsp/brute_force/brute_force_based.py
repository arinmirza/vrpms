from typing import List, Optional, Tuple

from src.tsp.brute_force.brute_force import solve
from src.utilities.vrp_helper import get_based_and_load_data

DEPOT = 0


def run(
    n: int = 8,
    per_km_time: float = 2,
    current_time: float = 0,
    current_location: int = DEPOT,
    ignore_long_trip: bool = False,
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param n: Number of locations
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param ignore_long_trip: Flag to ignore long trips
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    duration, _ = get_based_and_load_data(None, n, per_km_time)
    customers = [i for i in range(1, n) if i != current_location]
    return solve(current_time, current_location, customers, duration, ignore_long_trip)


if __name__ == "__main__":
    run()
