import random
from typing import Any, Dict, List, Tuple
from queue import PriorityQueue
from collections import defaultdict

N_TIME_ZONES = 12  # hours = time slices


class ACO_VRP:
    def __init__(
        self,
        n: int,
        m: int,
        consider_depot: bool,
        ignore_long_trip: bool,
        ignored_customers: List[int],
        vehicles_start_times: List[float],
        duration: List[List[List[float]]],
        load: List[int],
        hyperparams: Dict[str, Any],
    ):
        """
        Constructor of VRP with ACO

        :param n: Number of locations
        :param m: Max number of vehicles
        :param consider_depot: Consider depot as a candidate place to visit next
        :param ignore_long_trip: Flag to ignore long trips
        :param ignored_customers: List of customers to be ignored by the algorithm
        :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all
            assumed as zero.
        :param duration: Dynamic duration data
        :param load: Loads of locations
        :param hyperparams: Hyperparameter settings for the given best tour
        """
        self.n = n
        self.m = m
        self.consider_depot = consider_depot
        self.ignore_long_trip = ignore_long_trip
        self.ignored_customers = ignored_customers
        self.vehicles_start_times = vehicles_start_times
        self.duration = duration
        self.load = load
        self.N_ITERATIONS = hyperparams["N_ITERATIONS"]
        self.Q = hyperparams["Q"]
        self.ALPHA = hyperparams["ALPHA"]
        self.BETA = hyperparams["BETA"]
        self.RHO = hyperparams["RHO"]
        self.pheromone = self.init_pheromone()
        self.duration_power = self.init_duration_power()
        self.vehicles = PriorityQueue()

    def init_vehicles(self) -> None:
        """
        Initializes times of vehicles based on the given start times
        """
        while not self.vehicles.empty():
            self.vehicles.get()
        for i in range(self.m):
            self.vehicles.put((self.vehicles_start_times[i], i))

    def get_vehicle(self) -> Tuple[float, int]:
        """
        Gets the vehicle with the earliest available time

        :return: Vehicle available time and vehicle id
        """
        vehicle = self.vehicles.get()
        vehicle_t, vehicle_id = vehicle
        return vehicle_t, vehicle_id

    def put_vehicle(self, vehicle_t: float, vehicle_id: int) -> None:
        """
        Pushes the vehicle back to the PQ along with available time

        :param vehicle_t: Vehicle available time
        :param vehicle_id: Vehicle id
        """
        self.vehicles.put((vehicle_t, vehicle_id))

    def get_route_and_vehicle_times(self) -> Tuple[float, float, defaultdict]:
        """
        Gets the vehicle with the earliest available time

        :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver,
            the travel duration for each driver
        """
        vehicle_times = defaultdict(float)
        route_max_time, route_sum_time = 0, 0
        while not self.vehicles.empty():
            vehicle = self.vehicles.get()
            vehicle_t, vehicle_id = vehicle
            vehicle_times[vehicle_id] = vehicle_t
            route_max_time = vehicle_t
            route_sum_time += vehicle_t
        return route_max_time, route_sum_time, vehicle_times

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

    def init_pheromone(self) -> List[List[float]]:
        """
        Initialize pheromone values to be used while selecting next location to visit

        :return: Pheromone values to be used while selecting next location to visit
        """
        pheromone = []
        for i in range(self.n):
            pheromone_src = []
            for j in range(self.n):
                pheromone_src.append(1 / (self.n**2))
            pheromone.append(pheromone_src)
        return pheromone

    def check_unvisited_node_exists(self, visited: List[bool]) -> bool:
        """
        Checks if there is at least one unvisited location

        :param visited: Flags indicating that if a location is visited or not, for each location
        :return: Flag indicating that there is at least one unvisited location
        """
        for node, mark in enumerate(visited):
            if node > 0 and not mark and node not in self.ignored_customers:
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
            next_node = 0
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
        for i in range(self.n):
            for j in range(self.n):
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
        # Normalize
        sum_pheromone = 0
        for i in range(self.n):
            for j in range(self.n):
                sum_pheromone += self.pheromone[i][j]
        for i in range(self.n):
            for j in range(self.n):
                sum_pheromone /= sum_pheromone
