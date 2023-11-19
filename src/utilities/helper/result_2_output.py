from typing import Dict, List

DEPOT = 0  # depot
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60*60 seconds


def tsp_result_2_output(
    start_time: float, start_node: int, duration: List[List[List[float]]], locations: Dict, tsp_result: Dict
) -> Dict:
    route_time, route = tsp_result["route_time"], tsp_result["route"]
    tour = []
    current_node, current_time = start_node, start_time
    for node in route:
        location = locations[node]
        lat, lng = location["lat"], location["lng"]
        hour = int(current_time / TIME_UNITS)
        current_time += duration[current_node][node][hour]
        current_node = node
        tour.append({"lat": lat, "lng": lng, "arrivalTime": current_time})
    result = {"duration": route_time, "vehicle": tour}
    return result


def vrp_result_2_output(
    vehicles_start_times: List[float],
    duration: List[List[List[float]]],
    locations: Dict,
    vrp_result: Dict,
    capacities: List[int],
) -> Dict:
    m = len(vehicles_start_times)
    route_max_time = vrp_result["route_max_time"]
    route_sum_time = vrp_result["route_sum_time"]
    vehicles_routes = vrp_result["vehicles_routes"]
    vehicles_times = vrp_result["vehicles_times"]
    vehicles = []
    for vehicle_id in range(m):
        vehicle_tours = []
        if vehicle_id in vehicles_routes:
            vehicle_route = vehicles_routes[vehicle_id]
            current_node = DEPOT
            current_time = vehicles_times[vehicle_id]
            for cycle in vehicle_route:
                cycle_output = []
                for node in cycle:
                    location = locations[node]
                    lat, lng = location["lat"], location["lng"]
                    hour = int(current_time / TIME_UNITS)
                    current_time += duration[current_node][node][hour]
                    current_node = node
                    cycle_output.append({"lat": lat, "lng": lng, "arrivalTime": current_time})
                vehicle_tours.append(cycle_output)
        vehicle_dict = {
            "tours": vehicle_tours,
            "capacity": capacities[vehicle_id],
            "totalDuration": vehicles_times[vehicle_id],
        }
        vehicles.append(vehicle_dict)
    result = {"durationMax": route_max_time, "durationSum": route_sum_time, "vehicles": vehicles}
    return result
