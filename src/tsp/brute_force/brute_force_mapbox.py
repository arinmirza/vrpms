from typing import List, Optional, Tuple

from src.tsp.brute_force.brute_force import solve
from src.utilities.helper.data_helper import get_mapbox_and_local_data

DEPOT = 0


def run(
    n: int = 8,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    current_time: float = 0,
    current_location: int = DEPOT,
    ignore_long_trip: bool = False,
) -> Tuple[float, Optional[List[int]]]:
    """
    Calculates total time it takes to visit the locations and the route for the optimal solution

    :param n: Number of locations
    :param supabase_url: Project URL
    :param supabase_key: Project key
    :param supabase_url_key_file: Path of the file including supabase_url and supabase_key
    :param current_time: Current time
    :param current_location: Current (starting) location
    :param ignore_long_trip: Flag to ignore long trips
    :return: Total time it takes to visit the locations and the route for the optimal solution
    """
    assert current_location < n, "Current location should be in the fetched duration data"
    duration, _ = get_mapbox_and_local_data(supabase_url, supabase_key, supabase_url_key_file, None, n)
    customers = [i for i in range(1, n) if i != current_location]
    return solve(current_time, current_location, customers, duration, ignore_long_trip)


if __name__ == "__main__":
    run()
