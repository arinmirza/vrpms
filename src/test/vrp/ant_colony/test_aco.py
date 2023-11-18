from typing import List

from collections import defaultdict
from src.vrp.ant_colony.aco_hybrid import solve
from src.utilities.helper.data_helper import get_based_and_load_data, get_mapbox_and_load_data

EPS = 1e-6
TIME_UNITS = 3600  # hour = 60*60 seconds


def check_times(
    m: int,
    route_max_time: float,
    route_sum_time: float,
    vehicle_routes: defaultdict,
    vehicle_times: defaultdict,
    vehicles_start_times: List[float],
    duration: List[List[List[float]]],
) -> None:
    real_route_max_time, real_route_sum_time = 0, 0
    for vehicle_id in range(m):
        real_vehicle_t = vehicles_start_times[vehicle_id]
        if vehicle_id not in vehicle_routes:
            continue
        for path in vehicle_routes[vehicle_id]:
            path_len = len(path)
            for idx in range(1, path_len):
                hour = int(real_vehicle_t / TIME_UNITS)
                u, v = path[idx - 1], path[idx]
                real_vehicle_t += duration[u][v][hour]
        vehicle_t = vehicle_times[vehicle_id]
        print(real_vehicle_t, vehicle_t)
        assert abs(real_vehicle_t - vehicle_t) < EPS, f"Vehicle time should be {real_vehicle_t} instead of {vehicle_t}"
        real_route_max_time = max(real_route_max_time, real_vehicle_t)
        real_route_sum_time += real_vehicle_t
    assert (
        abs(real_route_max_time - route_max_time) < EPS
    ), f"Route max time should be {real_route_max_time} instead of {route_max_time}"
    assert (
        abs(real_route_sum_time - route_sum_time) < EPS
    ), f"Route sum time should be {real_route_sum_time} instead of {route_sum_time}"


def test_mapbox():
    n = 21
    m = 3
    route_max_time = 11320.919999999998
    route_sum_time = 31255.9
    vehicle_routes = {}
    vehicle_routes[0] = [[0, 2, 18, 19, 20, 3, 1, 0], [0, 10, 0]]
    vehicle_routes[1] = [[0, 17, 15, 14, 12, 11, 13, 0], [0, 5, 4, 7, 6, 8, 9, 0]]
    vehicle_routes[2] = [[0, 16, 0]]
    vehicle_times = {}
    vehicle_times[0] = 9081.67
    vehicle_times[1] = 10853.310000000001
    vehicle_times[2] = 11320.919999999998
    """
    route_max_time = 6679.639999999999
    route_sum_time = 19933.379999999997
    vehicle_routes = {}
    vehicle_routes[0] = [[0, 17, 16, 0]]
    vehicle_routes[1] = [[0, 8, 4, 7, 5, 6, 0], [0, 14, 11, 12, 13, 15, 0]]
    vehicle_routes[2] = [[0, 18, 3, 20, 10, 9, 1, 0], [0, 2, 19, 0]]
    vehicle_times = {}
    vehicle_times[0] = 6679.639999999999
    vehicle_times[1] = 6649.44
    vehicle_times[2] = 6604.299999999999
    """
    vehicles_start_times = [0 for _ in range(m)]
    supabase_url_key_file = "../../../../data/supabase/supabase_url_key.txt"
    duration, _ = get_mapbox_and_load_data(None, None, supabase_url_key_file, n)
    check_times(m, route_max_time, route_sum_time, vehicle_routes, vehicle_times, vehicles_start_times, duration)


def test_aco(n=26, m=3, k=5, q=5, per_km_time=2):
    vehicles_start_times = [0 for _ in range(m)]
    duration, load = get_based_and_load_data(None, n, per_km_time)
    results = solve(n=n, m=m, k=k, q=q, duration=duration, load=load, n_hyperparams=100, n_best_results=100)
    for result in results:
        route_max_time, route_sum_time, vehicle_routes, vehicle_times = result[:4]
        check_times(
            m=m,
            route_max_time=route_max_time,
            route_sum_time=route_sum_time,
            vehicle_routes=vehicle_routes,
            vehicle_times=vehicle_times,
            vehicles_start_times=vehicles_start_times,
            duration=duration,
        )


def test_aco_long_trip_per_km_time(n=26, m=3, k=5, q=5, per_km_time=100):
    duration, load = get_based_and_load_data(None, n, per_km_time)
    results = solve(
        n=n, m=m, k=k, q=q, duration=duration, load=load, n_hyperparams=100, n_best_results=100, ignore_long_trip=True
    )
    assert not results


def test_aco_long_trip_vehicles_start_times(n=26, m=3, k=5, q=5, per_km_time=1):
    duration, load = get_based_and_load_data(None, n, per_km_time)
    vehicles_start_times = [700 for _ in range(m)]
    results = solve(
        n=n,
        m=m,
        k=k,
        q=q,
        duration=duration,
        load=load,
        n_hyperparams=100,
        n_best_results=100,
        ignore_long_trip=True,
        vehicles_start_times=vehicles_start_times,
    )
    assert not results
