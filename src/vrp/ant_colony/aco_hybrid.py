import datetime

from src.vrp.ant_colony.aco_1 import ACO_VRP_1
from src.vrp.ant_colony.aco_2 import ACO_VRP_2
from src.vrp.ant_colony.aco_helper import get_hyperparams, print_sol
from src.utilities.vrp_helper import get_based_and_load_data, get_google_and_load_data

from typing import List, Literal, Optional

N_TIME_ZONES = 12  # hours = time slices

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def run(
    n: int = 26,
    m: int = 2,
    k: int = 5,
    q: int = 5,
    per_km_time: int = 1,
    n_hyperparams: int = 100,
    n_best_hyperparamas: int = 10,
    input_file_load: Optional[str] = None,
    use_google_data: bool = False,
    ignore_long_trip: bool = False,
    ignored_customers: Optional[List[int]] = None,
    vehicles_start_times: Optional[List[float]] = None,
    objective_func_type: Literal["min_max_time", "min_sum_time"] = "min_sum_time",
) -> None:
    """
    Gets input data, try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_hyperparamas: Number of best hyperparamater settings to print
    :param input_file_load: Path to the input file including loads (required capacities) of locations
    :param use_google_data: Flag to use Google Maps data or not
    :param ignore_long_trip: Flag to ignore long trips
    :param ignored_customers: List of customers to be ignored by the algorithm
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :param objective_func_type: Type of the objective function to minimize total time it takes to visit the locations
        for the latest driver or sum of the durations of each driver
    """
    objective_func_type = objective_func_type.lower()
    assert objective_func_type in [
        "min_max_time",
        "min_sum_time",
    ], f"{objective_func_type} as a function type is not implemented"

    if vehicles_start_times is None:
        vehicles_start_times = [0 for _ in range(m)]
    else:
        assert len(vehicles_start_times) == m, f"Size of the vehicles_start_times should be {m}"

    if ignored_customers is None:
        ignored_customers = []

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

    # aco_sols = [ACO_VRP_1, ACO_VRP_2]
    aco_sols = [ACO_VRP_1]
    add_depots = [False, True]
    results = []
    for hyperparams in all_hyperparams:
        for aco_sol in aco_sols:
            for add_depot in add_depots:
                vrp = aco_sol(
                    n=n,
                    m=m,
                    k=k,
                    q=q,
                    add_depot=add_depot,
                    ignore_long_trip=ignore_long_trip,
                    objective_func_type=objective_func_type,
                    ignored_customers=ignored_customers,
                    vehicles_start_times=vehicles_start_times,
                    duration=duration,
                    load=load,
                    hyperparams=hyperparams,
                )
                best_iter, route_max_time, route_sum_time, vehicle_routes, vehicle_times = vrp.solve()
                if iter is not None:
                    results.append(
                        (
                            route_max_time,
                            route_sum_time,
                            best_iter,
                            vehicle_routes,
                            vehicle_times,
                            hyperparams,
                            add_depot,
                            str(aco_sol),
                        )
                    )
    if objective_func_type == "min_max_time":
        results.sort(key=lambda x: x[0])
    else:
        results.sort(key=lambda x: x[1])

    time_end = datetime.datetime.now()

    for result_idx, result in reversed(list(enumerate(results[:n_best_hyperparamas]))):
        (
            route_max_time,
            route_sum_time,
            best_iter,
            vehicle_routes,
            vehicle_times,
            hyperparams,
            add_depot,
            aco_method,
        ) = result
        print_sol(
            result_idx=result_idx,
            best_iter=best_iter,
            route_max_time=route_max_time,
            route_sum_time=route_sum_time,
            vehicle_routes=vehicle_routes,
            vehicle_times=vehicle_times,
            hyperparams=hyperparams,
            add_depot=add_depot,
            aco_method=aco_method,
        )

    print(f"\nTime elapsed = {time_end-time_start}")


if __name__ == "__main__":
    run()
