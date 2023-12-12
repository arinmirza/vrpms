from typing import Dict, List

DEPOT = 0  # depot
TIME_UNITS = 3600  # hour = 60*60 seconds

LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_DEPOT_TIME_INIT = 30
UNLOADING_DEPOT_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def tsp_result_2_output(
    start_time: float,
    start_node: int,
    duration: List[List[List[float]]],
    load: List[int],
    locations: Dict,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
    tsp_result: Dict,
) -> Dict:
    # route_time = tsp_result["route_time"]
    route = tsp_result["route"]
    tour = []
    current_node, current_time = start_node, start_time

    for node_idx, node in enumerate(route):
        location = locations[node]
        lat, lng = location["lat"], location["lng"]
        hour = int(current_time / TIME_UNITS)
        current_time += duration[current_node][node][hour]
        tour.append({"lat": lat, "lng": lng, "arrivalTime": current_time})

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

    output = {"duration": current_time, "vehicle": tour}
    return output


def vrp_result_2_output(
    vehicles_start_times: List[float],
    duration: List[List[List[float]]],
    load: List[int],
    locations: Dict,
    vrp_result: Dict,
    capacities: List[int],
) -> Dict:
    m = len(vehicles_start_times)
    # route_max_time = vrp_result["route_max_time"]
    # route_sum_time = vrp_result["route_sum_time"]
    vehicles_routes = vrp_result["vehicles_routes"]
    # vehicles_times = vrp_result["vehicles_times"]
    vehicles = []
    route_max_time, route_sum_time = 0, 0
    for vehicle_id in range(m):
        vehicle_tours = []
        current_time = vehicles_start_times[vehicle_id]
        if vehicle_id in vehicles_routes:
            vehicle_route = vehicles_routes[vehicle_id]
            current_node = DEPOT
            for cycle in vehicle_route:
                cycle_output = []
                for node_idx, node in enumerate(cycle):
                    location = locations[node]
                    lat, lng = location["lat"], location["lng"]
                    hour = int(current_time / TIME_UNITS)
                    current_time += duration[current_node][node][hour]
                    cycle_output.append({"lat": lat, "lng": lng, "arrivalTime": current_time})
                    if node != DEPOT:
                        current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * load[node]
                    elif node_idx == 0:
                        total_load = 0
                        for customer in cycle:
                            total_load += load[customer]
                        if total_load > 0:
                            current_time += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load
                    current_node = node
                vehicle_tours.append(cycle_output)
        vehicle_dict = {
            "tours": vehicle_tours,
            "capacity": capacities[vehicle_id],
            "totalDuration": current_time,
        }
        route_sum_time += current_time
        route_max_time = max(route_max_time, current_time)
        vehicles.append(vehicle_dict)
    output = {"durationMax": route_max_time, "durationSum": route_sum_time, "vehicles": vehicles}
    return output