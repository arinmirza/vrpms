from typing import List, Tuple

DEPOT = 0
TIME_UNITS = 3600  # hour = 60*60 seconds

LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_DEPOT_TIME_INIT = 30
UNLOADING_DEPOT_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def route_solution_to_arrivals(
    vehicle_start_time: float,
    route: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    do_loading_unloading: bool,
    cancelled_customers: List[int],
) -> Tuple[List[float], float]:
    current_time = vehicle_start_time
    current_node = route[0]
    arrivals_cycle = []

    for node_idx, node in enumerate(route):
        hour = int(current_time / TIME_UNITS)
        current_time += duration[current_node][node][hour]
        arrivals_cycle.append(current_time)

        if node_idx == 0 and do_loading_unloading:
            if node != DEPOT:
                current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[node]
            else:
                total_load = 0
                for customer in route:
                    total_load += load[customer]
                if total_load > 0:
                    current_time += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load
        elif node_idx > 0:
            if node != DEPOT:
                current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[node]
            else:
                total_load = 0
                for customer in cancelled_customers:
                    total_load += load[customer]
                if total_load > 0:
                    current_time += UNLOADING_DEPOT_TIME_INIT + UNLOADING_DEPOT_TIME_PER_UNIT * total_load

        current_node = node

    return arrivals_cycle, current_time
