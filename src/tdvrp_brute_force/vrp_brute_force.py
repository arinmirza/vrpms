import itertools
from data_gen import get_dist_data
from datetime import datetime


K = 3
Q = 5 # number of max allowed shops per tour
VEHICLE_CAPACITY = 100
IGNORE_LONG_TRIP = True

INF = float("inf")
N_TIME_SLICES = 10
DEPOT = (0, -1, "Depot")
NODES = [
    (1, 40, "Olympia"),
    (2, 50, "Freisinger Landstraße 90"),
    (3, 30, "Infineon Campeon"),
    (4, 30, "Hauptbahnhof"),
    (5, 30, "Messestadt"),
    (6, 10, "IKEA Brunnthal"),
    (7, 10, "Nymphenburger Schloss")
]



def calculate_duration(perm, dist_data):
    """
        Calculates total time it takes to visit the locations in order and the route

        :param perm: The locations to visit in order
        :param dist_data: The locations to visit in order
    """
    perm = list(perm)
    perm.append(DEPOT)
    last_node = 0
    route = [last_node]
    curr_time, curr_capacity = 0, Q

    for elem in perm:
        node = elem[0]
        req_capacity = 0 if node == 0 else 1
        if node == 0 and last_node == 0:
            continue
        curr_time_slip = int(curr_time / 60)
        if not IGNORE_LONG_TRIP:
            curr_time_slip = min(curr_time_slip, N_TIME_SLICES-1)
        if curr_time_slip >= N_TIME_SLICES or curr_capacity < req_capacity:
            return INF, None
        curr_time += dist_data[last_node][node][curr_time_slip]
        if node == 0:
            curr_capacity = Q
        else:
            curr_capacity -= req_capacity
        last_node = node
        route.append(node)

    return curr_time, route


def run():
    """
        Calculates the duration of all permutations and returns the shortest one

    """
    start_time = datetime.now()
    dist_data = get_dist_data()

    for _ in range(K-1):
        NODES.append(DEPOT)
    best_dist, best_route = INF, None
    for perm in itertools.permutations(NODES):
        total_dist, route = calculate_duration(perm=perm, dist_data=dist_data)
        if route is not None and total_dist < best_dist:
            best_dist = total_dist
            best_route = route
    if best_route is None:
        print("No feasible solution")
    else:
        print(f"Total distance: {best_dist}")
        print(f"Best route: {best_route}")
    end_time = datetime.now()
    print(f"Time: {end_time-start_time}")
    pass

if __name__ == '__main__':
    run()
    pass
