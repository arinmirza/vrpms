from typing import Dict, List

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
