from typing import List

from collections import defaultdict
from src.vrp.ant_colony.aco_hybrid import solve
from src.utilities.helper.data_helper import get_based_and_load_data

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
        assert abs(real_vehicle_t - vehicle_t) < EPS, f"Vehicle time should be {real_vehicle_t} instead of {vehicle_t}"
        real_route_max_time = max(real_route_max_time, real_vehicle_t)
        real_route_sum_time += real_vehicle_t
    assert (
        abs(real_route_max_time - route_max_time) < EPS
    ), f"Route max time should be {real_route_max_time} instead of {route_max_time}"
    assert (
        abs(real_route_sum_time - route_sum_time) < EPS
    ), f"Route sum time should be {real_route_sum_time} instead of {route_sum_time}"


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
