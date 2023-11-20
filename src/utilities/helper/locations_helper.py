from typing import Dict, List, Tuple


def convert_locations(locations: List[Dict]) -> Dict:
    new_locations = {}
    for location in locations:
        new_locations[location["id"]] = location
    return new_locations


def get_available_and_all_ignored_customers(
    locations: Dict, ignored_customers: List[int], completed_customers: List[int], depot: int = 0
) -> Tuple[List[int], List[int]]:
    available_customers = []
    all_ignored_customers = []
    for key, location in locations.items():
        id, demand = location["id"], location["demand"]
        if id != depot:
            if id not in ignored_customers and id not in completed_customers:
                available_customers.append(id)
            else:
                all_ignored_customers.append(id)
    return available_customers, all_ignored_customers


def get_demands_from_locations(durations: List[List[List[float]]], locations: Dict, depot: int = 0) -> List[int]:
    n = len(durations)
    demands = [0 for _ in range(n)]
    for key, location in locations.items():
        id, demand = location["id"], location["demand"]
        if id < n and id != depot:
            demands[id] = demand
    return demands


def remove_unused_locations_vrp(
    locations: List[Dict], ignored_customers: List[int], completed_customers: List[int]
) -> List[Dict]:
    disregard = ignored_customers + completed_customers
    return [loc for loc in locations if loc["id"] not in disregard]


def remove_unused_locations_tsp(
    locations: List[Dict], customers: List[int], start_node: int, depot: int = 0
) -> List[Dict]:
    customers_ids = customers.copy()
    customers_ids.extend([start_node, depot])
    return [loc for loc in locations if loc["id"] in customers_ids]
