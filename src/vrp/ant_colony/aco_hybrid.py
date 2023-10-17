import datetime

from src.vrp.ant_colony.aco_1 import ACO_VRP_1
from src.vrp.ant_colony.aco_2 import ACO_VRP_2
from src.vrp.ant_colony.aco_helper import get_hyperparams, print_sol
from src.utilities.vrp_helper import get_based_and_load_data, get_google_and_load_data

from typing import Optional

N_TIME_ZONES = 12  # hours = time slices

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def run(
    n: int = 26,
    k: int = 5,
    q: int = 5,
    per_km_time: int = 1,
    n_hyperparams: int = 100,
    n_best_hyperparamas: int = 10,
    input_file_load: Optional[str] = None,
    use_google_data: bool = False,
    ignore_long_trip: bool = False,
) -> None:
    """
    Gets input data, try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_hyperparamas: Number of best hyperparamater settings to print
    :param input_file_load: Path to the input file including loads (required capacities) of locations
    :param use_google_data: Flag to use Google Maps data or not
    :param ignore_long_trip: Flag to ignore long trips
    """
    if use_google_data:
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)

    time_start = datetime.datetime.now()

    all_hyperparams = []
    for _ in range(n_hyperparams // 2):
        hyperparams = get_hyperparams()
        all_hyperparams.append(hyperparams)
        hyperparams_zero = hyperparams.copy()
        hyperparams_zero["Q"], hyperparams_zero["RHO"] = 0, 1
        all_hyperparams.append(hyperparams_zero)

    aco_sols = [ACO_VRP_1, ACO_VRP_2]
    add_depots = [False, True]
    results = []
    for hyperparams in all_hyperparams:
        for aco_sol in aco_sols:
            for add_depot in add_depots:
                vrp = aco_sol(n, k, q, ignore_long_trip, add_depot, duration, load, hyperparams)
                best_iter, vrp_route_cost, vrp_route = vrp.solve()
                if vrp_route is not None:
                    results.append((vrp_route_cost, best_iter, vrp_route, hyperparams, add_depot, str(aco_sol)))
    results.sort(key=lambda x: x[0])

    time_end = datetime.datetime.now()

    for result_idx, result in reversed(list(enumerate(results[:n_best_hyperparamas]))):
        vrp_route_cost, best_iter, vrp_route, hyperparams, add_depot, aco_method = result
        print_sol(
            result_idx,
            best_iter,
            vrp_route_cost,
            vrp_route,
            hyperparams,
            add_depot,
            aco_method,
        )

    print(f"\nTime elapsed = {time_end-time_start}")


if __name__ == "__main__":
    run()
