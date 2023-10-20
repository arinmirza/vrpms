from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from src.vrp.ant_colony.aco import ACO_VRP

DEPOT = 0  # id of the depot
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
TOTAL_TIME = N_TIME_ZONES * TIME_UNITS

INF = float("inf")


class ACO_VRP_1(ACO_VRP):
    def __init__(
        self,
        n: int,
        m: int,
        k: int,
        q: int,
        add_depot: bool,
        ignore_long_trip: bool,
        objective_func_type: str,
        ignored_customers: List[int],
        vehicles_start_times: List[float],
        duration: List[List[List[float]]],
        load: List[int],
        hyperparams: Dict[str, Any],
    ) -> None:
        """
        Constructor of VRP with ACO

        :param n: Number of locations
        :param m: Max number of vehicles
        :param k: Max number of cycles
        :param q: Capacity of vehicle
        :param add_depot: Add depot as a candidate place to visit next
        :param ignore_long_trip: Flag to ignore long trips
        :param ignored_customers: List of customers to be ignored by the algorithm
        :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all
            assumed as zero.
        :param objective_func_type: Type of the objective function to minimize total time it takes to visit the
            locations for the latest driver or sum of the durations of each driver
        :param duration: Dynamic duration data
        :param load: Loads of locations
        :param hyperparams: Hyperparameter settings for the given best tour
        """
        super().__init__(
            n, m, add_depot, ignore_long_trip, ignored_customers, vehicles_start_times, duration, load, hyperparams
        )
        self.k = k
        self.q = q
        self.objective_func_type = objective_func_type

    def __str__(self):
        return "ACO_1"

    def solve(self) -> Tuple[int, float, float, Optional[defaultdict], Optional[defaultdict]]:
        """
        Solves VRP problem by using ACO

        :return: Index of the best tour among iterations, total time it takes to visit the locations for the latest
            driver, sum of the durations of each driver, the routes for each driver, the travel duration for each driver
        """
        best_route_max_time, best_route_sum_time = INF, INF
        best_vehicle_routes, best_vehicle_times, best_iter = None, None, None
        # At each iteration, start over
        for iter_idx in range(self.N_ITERATIONS):
            self.init_vehicles()
            visited = [bool(i in self.ignored_customers) for i in range(self.n)]
            visited[0] = True
            fail = False
            vehicle_routes = defaultdict(list)
            ant_route_costs = []
            vrp_route = []
            # Fill each cycle
            for cycle_id in range(self.k):
                vehicle_t, vehicle_id = self.get_vehicle()
                finished = False
                capacity = self.q
                ant_route = [0]
                ant_route_cost = 0
                # Fill the cycle
                while not finished:
                    hour = int(vehicle_t / TIME_UNITS)
                    # Check if exceeds the time limit
                    if hour >= N_TIME_ZONES:
                        if self.ignore_long_trip:
                            fail = True
                            finished = True
                            continue
                        else:
                            hour = N_TIME_ZONES - 1
                    ant_node = ant_route[-1]
                    nodes = []
                    # Fetch unvisited nodes where it is possible to visit next considering load constraints
                    for node in range(self.n):
                        if node not in self.ignored_customers:
                            if (capacity >= self.load[node] and not visited[node]) or (
                                ant_node != DEPOT and node == DEPOT and self.add_depot
                            ):
                                nodes.append(node)
                    # Get the next node based on pheromones
                    next_node = self.get_next_node(nodes, ant_node, hour) if nodes else 0
                    visited[next_node] = True
                    capacity -= self.load[next_node]
                    ant_route.append(next_node)
                    vehicle_t += self.duration[ant_node][next_node][hour]
                    ant_route_cost += self.duration[ant_node][next_node][hour]  # hour = 0 can be considered
                    finished = bool(next_node == 0)
                # Check if exceeds the time limit
                if fail:
                    break
                else:
                    self.put_vehicle(vehicle_t, vehicle_id)
                    vrp_route.append(ant_route)
                    vehicle_routes[vehicle_id].append(ant_route)
                    ant_route_costs.append(ant_route_cost)
            # Check if exceeds the time limit
            if self.check_unvisited_node_exists(visited):
                fail = True
            if not fail:
                # Check if it is the best
                route_max_time, route_sum_time, vehicle_times = self.get_route_and_vehicle_times()
                if self.ignore_long_trip and route_max_time >= N_TIME_ZONES * TIME_UNITS:
                    continue
                if (self.objective_func_type == "min_max_time" and route_max_time < best_route_max_time) or (
                    self.objective_func_type == "min_sum_time" and route_sum_time < best_route_sum_time
                ):
                    best_iter = iter_idx
                    best_route_max_time = route_max_time
                    best_route_sum_time = route_sum_time
                    best_vehicle_routes = vehicle_routes
                    best_vehicle_times = vehicle_times
                self.update_pheromone(vrp_route, ant_route_costs)
        return best_iter, best_route_max_time, best_route_sum_time, best_vehicle_routes, best_vehicle_times
