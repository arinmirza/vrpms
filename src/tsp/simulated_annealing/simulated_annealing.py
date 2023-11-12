import math
import random
from datetime import datetime
from typing import List, Literal, Optional, Tuple, Union

from src.tsp.simulated_annealing.simulated_annealing_helper import (
    update_tour_with_2opt,
    update_tour_with_exchange,
    compute_nearest_neighbor_tour,
    compute_successive_insertion_tour,
    compute_random_tour,
)
from src.utilities.helper.data_helper import (
    get_based_and_load_data,
    get_google_and_load_data,
    get_mapbox_and_local_data,
)

DEPOT = 0
N_TIME_ZONES = 12
INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]


def simulated_annealing_iterations(
    distance: List[List[List[float]]],
    tour: List[int],
    n_iterations: int,
    neighborhood: Literal["2-opt", "exchange"],
    temperature: float,
    length: float,
    best_tour: List[int],
    best_length: float,
    start_time: float,
) -> Tuple[float, List[int], float, List[int]]:
    neighborhood = neighborhood.lower()
    assert neighborhood in ["2-opt", "exchange"], "Neighborhood method is not valid"
    n_tour_nodes = len(tour)
    for _ in range(n_iterations):
        if neighborhood == "2-opt":
            i = random.randrange(n_tour_nodes - 3)
            j = random.randrange(i + 2, n_tour_nodes - 1)
            new_length, new_tour = update_tour_with_2opt(tour=tour, i=i, j=j, distance=distance, start_time=start_time)
        elif neighborhood == "exchange":
            i = random.randrange(1, n_tour_nodes - 2)
            j = random.randrange(i + 1, n_tour_nodes - 1)
            new_length, new_tour = update_tour_with_exchange(
                tour=tour, i=i, j=j, distance=distance, start_time=start_time
            )
        else:
            raise ValueError(f"Method {neighborhood} is not allowed. Options: '2-opt', 'exchange'")
        delta = length - new_length
        if delta > 0 or (random.random() < math.exp(delta / temperature)):
            tour, length = new_tour, new_length
        if length < best_length:
            best_length = length
            best_tour = tour
    return length, tour, best_length, best_tour


def simulated_annealing(
    distance: List[List[List[float]]],
    tour: List[int],
    length: float,
    init_temperature: float,
    threshold: Union[int, float],
    n_iterations: int,
    cooling: float,
    termination: Literal["max_steps", "min_temp"],
    neighborhood: Literal["2-opt", "exchange"],
    start_time: float,
) -> Tuple[float, List[int]]:
    termination = termination.lower()
    assert termination in ["max_steps", "min_temp"], "Termination method is not valid"
    best_tour, best_length = tour, length
    temperature = init_temperature
    step = 0
    while True:
        length, tour, best_length, best_tour = simulated_annealing_iterations(
            distance=distance,
            tour=tour,
            n_iterations=n_iterations,
            neighborhood=neighborhood,
            temperature=temperature,
            length=length,
            best_tour=best_tour,
            best_length=best_length,
            start_time=start_time,
        )
        if termination == "max_steps":
            step += 1
            if step == threshold:
                break
        elif termination == "min_temp":
            temperature *= cooling
            if temperature < threshold:
                break
        else:
            raise ValueError(f"Method {termination} is not allowed. Options: 'max_steps', 'min_temp'")
    return best_length, best_tour


def solve(
    distance: List[List[List[float]]],
    threshold: Union[int, float],
    n_iterations: int,
    alpha: float,
    cooling: float,
    init: Literal["nearest_neighbor", "successive_insertion", "random"],
    termination: Literal["max_steps", "min_temp"],
    neighborhood: Literal["2-opt", "exchange"],
    customers: List[int],
    start_node: int,
    start_time: float,
) -> Tuple[float, List[int]]:
    init = init.lower()
    assert init in ["nearest_neighbor", "successive_insertion", "random"], "Init method is not valid"
    if init == "nearest_neighbor":
        length, tour = compute_nearest_neighbor_tour(
            customers=customers, start_node=start_node, distance=distance, start_time=start_time
        )
    elif init == "successive_insertion":
        length, tour = compute_successive_insertion_tour(
            customers=customers, start_node=start_node, distance=distance, start_time=start_time
        )
    elif init == "random":
        length, tour = compute_random_tour(
            customers=customers, start_node=start_node, distance=distance, start_time=start_time
        )
    else:
        raise ValueError(f"Method {init} is not allowed. Options: 'nearest_neighbor', 'nearest_neighbor', 'random'")
    init_temperature = length * alpha
    best_length, best_tour = simulated_annealing(
        distance=distance,
        tour=tour,
        length=length,
        init_temperature=init_temperature,
        threshold=threshold,
        n_iterations=n_iterations,
        cooling=cooling,
        termination=termination,
        neighborhood=neighborhood,
        start_time=start_time,
    )
    return best_length, best_tour


def run(
    n: int = 8,
    current_time: float = 0,
    current_location: int = DEPOT,
    threshold: Union[int, float] = 10,
    n_iterations: int = 100,
    alpha: float = 0.1,
    cooling: float = 0.9,
    init: Literal["nearest_neighbor", "successive_insertion", "random"] = "nearest_neighbor",
    termination: Literal["max_steps", "min_temp"] = "max_steps",
    neighborhood: Literal["2-opt", "exchange"] = "2-opt",
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    per_km_time: int = 1,
    duration_data_type: Literal["mapbox", "google", "based"] = "mapbox",
) -> Tuple[float, List[int]]:
    assert current_location < n, "Start node should be in the fetched duration data"
    duration_data_type = duration_data_type.lower()
    assert duration_data_type in ["mapbox", "google", "based"], "Duration data type is not valid"
    start_time = datetime.now()
    if duration_data_type == "mapbox":
        duration, _ = get_mapbox_and_local_data(supabase_url, supabase_key, supabase_url_key_file, None, n)
    elif duration_data_type == "google":
        duration, _ = get_google_and_load_data(INPUT_FILES_TIME, None, n)
    elif duration_data_type == "based":
        duration, _ = get_based_and_load_data(None, n, per_km_time)
    else:
        raise ValueError(f"Method {duration_data_type} is not allowed. Options: 'mapbox', 'google', 'based'")
    customers = [i for i in range(1, n) if i != current_location]
    best_length, best_tour = solve(
        distance=duration,
        threshold=threshold,
        n_iterations=n_iterations,
        alpha=alpha,
        cooling=cooling,
        init=init,
        termination=termination,
        neighborhood=neighborhood,
        customers=customers,
        start_node=current_location,
        start_time=current_time,
    )
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")
    print(f"Best route time: {best_length}")
    print(f"Best route: {best_tour}")
    return best_length, best_tour


if __name__ == "__main__":
    run()
