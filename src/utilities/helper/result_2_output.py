from typing import Dict, List

N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60*60 seconds


def tsp_result_2_output(
    start_time: float, start_node: int, duration: List[List[List[float]]], locations: Dict, result: Dict
) -> Dict:
    route_time, route = result["route_time"], result["route"]
    tour = []
    current_node, current_time = start_node, start_time
    for node in route:
        lat, lng = locations[node]["lat"], lng = locations[node]["lng"]
        hour = int(current_time / TIME_UNITS)
        current_time += duration[current_node][node][hour]
        current_node = node
        tour.append({"lat": lat, "lng": lng, "arrivalTime": current_time})
    output = {"tour": tour, "totalDuration": route_time}
    return output
