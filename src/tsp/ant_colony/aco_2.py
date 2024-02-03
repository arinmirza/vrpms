from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from src.tsp.ant_colony.aco import ACO_TSP

DEPOT = 0  # id of the depot
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60*60 seconds
TOTAL_TIME = N_TIME_ZONES * TIME_UNITS

INF = float("inf")


class ACO_TSP_2(ACO_TSP):
    def __init__(
        self,
        n: int,
        pheromone_use_first_hour: bool,
        ignore_long_trip: bool,
        customers: List[int],
        start_time: float,
        start_node: int,
        duration: List[List[List[float]]],
        hyperparams: Dict[str, Any],
    ) -> None:
        """
        Constructor of VRP with ACO

        :param n: Number of locations
        :param pheromone_use_first_hour: Consider first hour of duration data for pheromone calculations
        :param ignore_long_trip: Flag to ignore long trips
        :param customers: List of customers to be visited
        :param start_time: Start time of the vehicle
        :param start_node: First node of the tour
        :param duration: Dynamic duration data
        :param hyperparams: Hyperparameter settings for the given best tour
        """
        super().__init__(
            n=n,
            pheromone_use_first_hour=pheromone_use_first_hour,
            ignore_long_trip=ignore_long_trip,
            customers=customers,
            start_time=start_time,
            start_node=start_node,
            duration=duration,
            hyperparams=hyperparams,
        )
        self.N_SUB_ITERATIONS = hyperparams["N_SUB_ITERATIONS"]

    def __str__(self):
        return "ACO_2"

    def solve(self) -> Tuple[float, Optional[List], Optional[int]]:
        """
        Solves VRP problem by using ACO (2nd method)

        :return: ...
        """
        best_route_time, best_route, best_iter = INF, None, None
        # At each iteration, start over
        for iter_idx in range(self.N_ITERATIONS):
            pheromone_paths, pheromone_paths_costs = [], []
            for _ in range(self.N_SUB_ITERATIONS):
                visited = [False for _ in range(self.n)]
                visited[self.start_node] = True
                fail = False
                pheromone_path, pheromone_path_cost = [self.start_node], 0
                vehicle_t = self.start_time
                finished = False
                last_node = self.start_node
                while not finished:
                    hour = int(vehicle_t / TIME_UNITS)
                    # Check if exceeds the time limit
                    if not self.ignore_long_trip:
                        hour = min(hour, N_TIME_ZONES - 1)
                    if hour >= N_TIME_ZONES:
                        fail = True
                        break
                    # Fetch unvisited nodes where it is possible to visit next
                    nodes = [node for node in self.customers if not visited[node]]
                    # Get the next node based on pheromones
                    next_node = self.get_next_node(nodes, last_node, hour) if nodes else DEPOT
                    visited[next_node] = True
                    pheromone_path.append(next_node)
                    vehicle_t += self.duration[last_node][next_node][hour]
                    pheromone_hour = 0 if self.pheromone_use_first_hour else hour
                    pheromone_path_cost += self.duration[last_node][next_node][pheromone_hour]
                    finished = bool(next_node == DEPOT)
                    last_node = next_node
                if self.check_unvisited_node_exists(visited):
                    fail = True
                if not fail:
                    pheromone_paths.append(pheromone_path)
                    pheromone_paths_costs.append(pheromone_path_cost)
                    # Check if it is the best among sub-iterations
                    if self.ignore_long_trip and vehicle_t >= N_TIME_ZONES * TIME_UNITS:
                        continue
                    if vehicle_t < best_route_time:
                        best_iter = iter_idx
                        best_route_time = vehicle_t
                        best_route = pheromone_path
            # Check if it is the best among iterations
            if pheromone_paths:
                self.update_pheromone(pheromone_paths, pheromone_paths_costs)
        return best_route_time, best_route, best_iter
