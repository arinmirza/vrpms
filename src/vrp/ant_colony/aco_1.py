from typing import Any, Dict, List, Optional, Tuple

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
        init_capacity: int,
        add_depot: bool,
        ignore_long_trip: bool,
        duration: List[List[List[float]]],
        load: List[int],
        hyperparams: Dict[str, Any],
    ) -> None:
        """
        Constructor of VRP with ACO

        :param n: Number of locations
        :param m: Max number of cycles
        :param init_capacity: Capacity of vehicle
        :param add_depot: Add depot as a candidate place to visit next
        :param ignore_long_trip: Flag to ignore long trips
        :param duration: Dynamic duration data
        :param load: Loads of locations
        :param hyperparams: Hyperparameter settings for the given best tour
        """
        super().__init__(n, m, init_capacity, add_depot, ignore_long_trip, duration, load, hyperparams)

    def __str__(self) -> str:
        return "ACO_1"

    def solve(self) -> Tuple[int, Optional[float], Optional[List[List[int]]]]:
        """
        Solves VRP problem by using ACO

        :return: Index of the best tour among iterations, total cost of the best tour and locations in the best tour,
            in order
        """
        all_vrp_route_costs, all_vrp_routes = [], []
        best_vrp_route_cost, best_vrp_route = INF, None
        best_iter = None
        # At each iteration, start over
        for iter_idx in range(self.N_ITERATIONS):
            visited = [False for _ in range(self.n)]
            visited[0] = True
            fail = False
            vrp_route = []
            vrp_route_cost = 0
            ant_route_costs = []
            # Fill each cycle
            for _ in range(self.m):
                finished = False
                capacity = self.init_capacity
                ant_route = [0]
                ant_route_cost = 0
                # Fill the cycle
                while not finished:
                    hour = int(vrp_route_cost / TIME_UNITS)
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
                        if (capacity >= self.load[node] and not visited[node]) or (node == DEPOT and self.add_depot):
                            nodes.append(node)
                    # Get the next node based on pheromones
                    next_node = self.get_next_node(nodes, ant_node, hour) if nodes else 0
                    visited[next_node] = True
                    capacity -= self.load[next_node]
                    ant_route.append(next_node)
                    vrp_route_cost += self.duration[ant_node][next_node][hour]
                    ant_route_cost += self.duration[ant_node][next_node][hour]
                    finished = next_node == 0
                # Check if exceeds the time limit
                if fail:
                    break
                else:
                    vrp_route.append(ant_route)
                    ant_route_costs.append(ant_route_cost)
            # Check if exceeds the time limit
            if vrp_route_cost >= TOTAL_TIME and self.ignore_long_trip:
                fail = True
            elif self.check_unvisited_node_exists(visited):
                fail = True
            if not fail:
                # Add to solutions
                all_vrp_route_costs.append(vrp_route_cost)
                all_vrp_routes.append(vrp_route)
                # Check if it is the best
                if vrp_route_cost < best_vrp_route_cost:
                    best_iter = iter_idx
                    best_vrp_route_cost = vrp_route_cost
                    best_vrp_route = vrp_route
                self.update_pheromone(vrp_route, ant_route_costs)
        return best_iter, best_vrp_route_cost, best_vrp_route
