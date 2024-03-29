import random
from typing import Any, Dict, List

DEPOT = 0  # depot
N_TIME_ZONES = 12  # hours = time slices


class ACO_TSP:
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
    ):
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
        self.n = n
        self.pheromone_use_first_hour = pheromone_use_first_hour
        self.ignore_long_trip = ignore_long_trip
        self.customers = customers
        self.customers_and_depot = customers.copy()
        self.customers_and_depot.append(DEPOT)
        if start_node != DEPOT:
            self.customers_and_depot.append(start_node)
        self.start_time = start_time
        self.start_node = start_node
        self.duration = duration
        self.N_ITERATIONS = hyperparams["N_ITERATIONS"]
        self.Q = hyperparams["Q"]
        self.ALPHA = hyperparams["ALPHA"]
        self.BETA = hyperparams["BETA"]
        self.RHO = hyperparams["RHO"]
        self.pheromone = self.init_pheromone()
        self.duration_power = self.init_duration_power()

    def init_duration_power(self) -> List[List[List[float]]]:
        """
        Calculates power of duration values to be used while selecting next location to visit

        :return: Power of duration values to be used while selecting next location to visit
        """
        duration_power = []
        for i in range(self.n):
            duration_power_src = []
            for j in range(self.n):
                duration_power_src_dest = []
                for t in range(N_TIME_ZONES):
                    duration_power_src_dest.append(self.duration[i][j][t] ** self.BETA)
                duration_power_src.append(duration_power_src_dest)
            duration_power.append(duration_power_src)
        return duration_power

    def normalize_pheromone(self, pheromone: List[List[float]]) -> None:
        # Normalize
        sum_pheromone = 0
        for i in self.customers_and_depot:
            for j in self.customers_and_depot:
                sum_pheromone += pheromone[i][j]
        for i in self.customers_and_depot:
            for j in self.customers_and_depot:
                pheromone[i][j] /= sum_pheromone

    def init_pheromone(self) -> List[List[float]]:
        """
        Initialize pheromone values to be used while selecting next location to visit

        :return: Pheromone values to be used while selecting next location to visit
        """
        pheromone = []
        for i in range(self.n):
            pheromone_src = []
            for j in range(self.n):
                pheromone_val_src = int(i in self.customers_and_depot)
                pheromone_val_dest = int(j in self.customers_and_depot)
                pheromone_src.append(pheromone_val_src * pheromone_val_dest)
            pheromone.append(pheromone_src)
        self.normalize_pheromone(pheromone)
        return pheromone

    def check_unvisited_node_exists(self, visited: List[bool]) -> bool:
        """
        Checks if there is at least one unvisited location

        :param visited: Flags indicating that if a location is visited or not, for each location
        :return: Flag indicating that there is at least one unvisited location
        """
        for node in self.customers:
            if not visited[node]:
                return True
        return False

    def get_next_node(self, nodes: List[int], ant_node: int, hour: int) -> int:
        """
        Finds the best next location to visit based on the pheromone formula. For more information on location choice:
            https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

        :param nodes: Unvisited nodes in the current tour
        :param ant_node: ID of the ant
        :param hour: Current hour (time zone/slice)
        :return: Next location to visit
        """
        sum_probs = 0
        probs = [0 for _ in range(self.n)]
        for node in nodes:
            probs[node] = (self.pheromone[ant_node][node] ** self.ALPHA) / self.duration_power[ant_node][node][hour]
            # Sum up the values to calculate normalizing factor
            sum_probs += probs[node]
        if sum_probs is None or sum_probs == 0:
            next_node = DEPOT
        else:
            # Normalize to get actual probs
            for node in nodes:
                probs[node] /= sum_probs
            curr_sum = 0
            next_node, last_next_node_candidate = None, None
            random_prob = random.uniform(0, 1)
            # Fetch the next node based on probs
            for node in nodes:
                last_next_node_candidate = node
                curr_sum += probs[node]
                if curr_sum >= random_prob:
                    next_node = node
                    break
            if next_node is None:
                next_node = last_next_node_candidate
        return next_node

    def update_pheromone(self, paths: List[List[int]], paths_costs: List[float]) -> None:
        """
        Updates pheromone values to be used while selecting next location to visit. For more information on update:
            https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

        :param paths: Paths for each ant
        :param paths_costs: Costs for each path
        """
        # Multiply with rho
        for i in self.customers_and_depot:
            for j in self.customers_and_depot:
                self.pheromone[i][j] *= self.RHO
        # Update based on the paths
        n_paths = len(paths)
        for path_id in range(n_paths):
            path = paths[path_id]
            path_len = len(path)
            path_cost = paths_costs[path_id]
            for idx in range(1, path_len):
                u, v = path[idx - 1], path[idx]
                if u != v:
                    self.pheromone[u][v] += self.Q / path_cost
        self.normalize_pheromone(self.pheromone)
