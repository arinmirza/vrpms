import random
from typing import Any, Dict, List, Optional, Tuple

N_TIME_ZONES = 12  # hours = time slices


class ACO_VRP:
    def __init__(
        self,
        n: int,
        m: int,
        init_capacity: int,
        duration: List[List[List[float]]],
        load: List[int],
        hyperparams: Dict[str, Any],
    ):
        """
        Constructor of VRP with ACO

        :param n: Number of locations
        :param m: Max number of cycles
        :param init_capacity: Capacity of vehicle
        :param duration: Dynamic duration data
        :param load: Loads of locations
        :param hyperparams: Hyperparameter settings for the given best tour
        """
        self.n = n
        self.m = m
        self.init_capacity = init_capacity
        self.duration = duration
        self.load = load
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

    @staticmethod
    def check_unvisited_node_exists(visited: List[bool]) -> bool:
        """
        Checks if there is at least one unvisited location

        :param visited: Flags indicating that if a location is visited or not, for each location
        :return: Flag indicating that there is at least one unvisited location
        """
        for mark in visited:
            if not mark:
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
