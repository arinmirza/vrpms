from typing import Any, Dict, List, Literal, Optional, Tuple

from src.vrp.ant_colony.aco import ACO_VRP

DEPOT = 0  # id of the depot
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
TOTAL_TIME = N_TIME_ZONES * TIME_UNITS

INF = float("inf")


class ACO_VRP_2(ACO_VRP):
    def __init__(
        self,
        n: int,
        m: int,
        k: int,
        q: int,
        add_depot: bool,
        ignore_long_trip: bool,
        ignored_customers: List[int],
        vehicles_start_times: List[float],
        objective_func_type: Literal["min_max_time", "min_sum_time"],
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
            n,
            m,
            add_depot,
            ignore_long_trip,
            ignored_customers,
            vehicles_start_times,
            duration,
            load,
            hyperparams,
        )
        self.k = k
        self.q = q
        self.objective_func_type = objective_func_type
        self.N_SUB_ITERATIONS = hyperparams["N_SUB_ITERATIONS"]

    def __str__(self):
        return "ACO_2"

    @staticmethod
    def split_path_to_cycles(path: List[int]) -> List[List[int]]:
        """
        Parses a given path to the cycles

        :param path: Path to be parsed
        :return: Cycles given in the path
        """
        indices = [idx for idx, node in enumerate(path) if node == 0]
        n_zeroes = len(indices)
        cycles = []
        for i in range(n_zeroes - 1):
            idx_l, idx_r = indices[i], indices[i + 1]
            cycle = path[idx_l : idx_r + 1]
            cycles.append(cycle)
        return cycles

    def solve(self) -> Tuple[int, Optional[float], Optional[List[List[int]]]]:
        """
        Solves VRP problem by using ACO

        :return: Index of the best tour among iterations, total cost of the best tour and locations in the best tour,
            in order
        """
        best_of_best_cost = INF
        best_of_best_route = None
        best_iter = None
        # At each iteration, start over
        for iter_idx in range(self.N_ITERATIONS):
            best_ant_route = None
            best_ant_route_cost = INF
            ant_routes = []
            ant_route_costs = []
            for _ in range(self.N_SUB_ITERATIONS):
                visited = [False for _ in range(self.n)]
                visited[0] = True
                fail = False
                vrp_route = [0]
                vrp_route_cost = 0
                n_tours = 0
                capacity = self.q
                # Check if constraint based on the number of cycles satisfied
                while n_tours < self.k:
                    hour = int(vrp_route_cost / TIME_UNITS)
                    # Check if exceeds the time limit
                    if hour >= N_TIME_ZONES:
                        if self.ignore_long_trip:
                            fail = True
                            break
                        else:
                            hour = N_TIME_ZONES - 1
                    ant_node = vrp_route[-1]
                    nodes = []
                    # Fetch unvisited nodes to visit next
                    for node in range(self.n):
                        if node not in self.ignored_customers:
                            if (capacity >= self.load[node] and not visited[node]) or (
                                ant_node != DEPOT and node == DEPOT and self.add_depot
                            ):
                                nodes.append(node)
                    # Get the next node based on pheromones
                    next_node = self.get_next_node(nodes, ant_node, hour) if nodes else 0
                    if next_node != 0:
                        # Keep the cycle, add the node to the current cycle
                        capacity -= self.load[next_node]
                        vrp_route.append(next_node)
                        visited[next_node] = True
                        vrp_route_cost += self.duration[ant_node][next_node][hour]
                    else:
                        # Finish the cycle by adding the depot
                        next_node = 0
                        n_tours += 1
                        vrp_route.append(next_node)
                        capacity = self.q
                        vrp_route_cost += self.duration[ant_node][next_node][hour]
                # Check if exceeds the time limit
                if vrp_route_cost >= TOTAL_TIME and self.ignore_long_trip:
                    fail = True
                elif self.check_unvisited_node_exists(visited):
                    fail = True
                if not fail:
                    # Add to solutions
                    ant_routes.append(vrp_route)
                    ant_route_costs.append(vrp_route_cost)
                    # Check if it is the best among sub-iterations
                    if vrp_route_cost < best_ant_route_cost:
                        best_ant_route_cost = vrp_route_cost
                        best_ant_route = vrp_route
            # Check if it is the best among iterations
            if best_ant_route is not None:
                if best_ant_route_cost < best_of_best_cost:
                    best_iter = iter_idx
                    best_of_best_cost = best_ant_route_cost
                    best_of_best_route = best_ant_route
                self.update_pheromone(ant_routes, ant_route_costs)
        if best_of_best_route is not None:
            best_of_best_route = self.split_path_to_cycles(best_of_best_route)
        return best_iter, best_of_best_cost, best_of_best_route
