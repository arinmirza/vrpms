from typing import List

from src.vrp.brute_force.brute_force import run


def test_vehicles_start_times(m: int = 2, vehicles_start_times: List[float] = [60, 120]):
    max_time_early, sum_time_early, vehicle_routes_early, vehicle_times_early = run(duration_data_type="based")
    max_time_late, sum_time_late, vehicle_routes_late, vehicle_times_late = run(
        m=m, vehicles_start_times=vehicles_start_times, duration_data_type="based"
    )
    assert max_time_early <= max_time_late
    assert sum_time_early <= sum_time_late


def test_ignored_customers(ignored_customers: List[int] = [1, 2, 3]):
    _, _, vehicle_routes, _ = run(ignored_customers=ignored_customers, duration_data_type="based")
    for vehicle_id, vehicle_cycles in vehicle_routes.items():
        for cycle in vehicle_cycles:
            common_nodes = list(set(cycle) & set(ignored_customers))
            assert len(common_nodes) == 0
