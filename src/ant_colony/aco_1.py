import datetime
import random
from typing import Any, Dict, List, Optional, Tuple

from src.ant_colony.aco_helper import get_hyperparams, print_sol_1
from src.utilities.vrp_helper import (get_based_and_load_data,
                                      get_google_and_load_data)

N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
TOTAL_TIME = N_TIME_ZONES * TIME_UNITS
IGNORE_LONG_TRIP = True

INPUT_FOLDER_PATH = "../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [
    f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt"
    for hour in range(N_TIME_ZONES)
]

RANGE_N_ITERATIONS = (100, 1000)
RANGE_Q = (1, 1000)
RANGE_ALPHA = (2, 5)
RANGE_BETA = (2, 5)
RANGE_RHO = (0.8, 1)

INF = float("inf")


class VRP:
    def __init__(
        self,
        n: int,
        m: int,
        init_capacity: int,
        duration: List[List[List[float]]],
        load: List[int],
        hyperparams: Dict[str, Any],
    ) -> None:
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
        for t in range(N_TIME_ZONES):
            duration_power_t = []
            for i in range(self.n):
                duration_power_t_src = []
                for j in range(self.n):
                    duration_power_t_src.append(self.duration[t][i][j] ** self.BETA)
                duration_power_t.append(duration_power_t_src)
            duration_power.append(duration_power_t)
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

    def update_pheromone(
        self, vrp_route: List[List[int]], ant_route_costs: List[float]
    ) -> None:
        """
        Updates pheromone values to be used while selecting next location to visit. For more information on update:
            https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

        :param vrp_route: Completed VRP tour, including visited locations in order
        :param ant_route_costs: Costs for each ant
        """
        for i in range(self.n):
            for j in range(self.n):
                self.pheromone[i][j] *= self.RHO
        for ant_id in range(self.m):
            ant_route = vrp_route[ant_id]
            ant_route_len = len(ant_route)
            ant_route_cost = ant_route_costs[ant_id]
            if ant_route_len > 2:
                for idx in range(ant_route_len):
                    u, v = ant_route[idx - 1], ant_route[idx]
                    self.pheromone[u][v] += self.Q / ant_route_cost

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
            probs[node] = (
                self.pheromone[ant_node][node] ** self.ALPHA
            ) / self.duration_power[hour][ant_node][node]
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

    def solve(self) -> Tuple[int, float, List[List[int]]]:
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
                        if IGNORE_LONG_TRIP:
                            fail = True
                            finished = True
                            continue
                        else:
                            hour = N_TIME_ZONES - 1
                    ant_node = ant_route[-1]
                    nodes = []
                    # Fetch unvisited nodes where it is possible to visit next considering load constraints
                    for node in range(self.n):
                        if not visited[node] and capacity >= self.load[node]:
                            nodes.append(node)
                    # Get the next node based on pheromones
                    next_node = (
                        self.get_next_node(nodes, ant_node, hour) if nodes else 0
                    )
                    visited[next_node] = True
                    capacity -= self.load[next_node]
                    ant_route.append(next_node)
                    vrp_route_cost += self.duration[hour][ant_node][next_node]
                    ant_route_cost += self.duration[hour][ant_node][next_node]
                    finished = next_node == 0
                # Check if exceeds the time limit
                if fail:
                    break
                else:
                    vrp_route.append(ant_route)
                    ant_route_costs.append(ant_route_cost)
            # Check if exceeds the time limit
            if not fail:
                if vrp_route_cost > TOTAL_TIME or self.check_unvisited_node_exists(
                    visited
                ):
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


# input_file_load: "../../../data/loads/data_load.txt"
def run(
    n: int = 8,
    k: int = 3,
    q: int = 5,
    per_km_time: int = 5,
    n_hyperparams: int = 100,
    n_best_hyperparamas: int = 3,
    input_file_load: Optional[str] = None,
    use_google_data: bool = False,
) -> None:
    """
    Gets input data, try different hyperparamater settings and solve VRP with ACO

    :param n: Number of locations
    :param k: Max number of cycles
    :param q: Capacity of vehicle
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param n_hyperparams: Number of hyperparamater settings to try
    :param n_best_hyperparamas: Number of best hyperparamater settings to print
    :param input_file_load: Path to the input file including loads (required capacities) of locations
    :param use_google_data: Flag to use Google Maps data or not
    """
    if use_google_data:
        duration, load = get_google_and_load_data(
            INPUT_FILES_TIME, input_file_load, n, False
        )
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time, False)
    time_start = datetime.datetime.now()
    all_hyperparams = []
    for _ in range(n_hyperparams // 2):
        hyperparams = get_hyperparams(
            RANGE_N_ITERATIONS, RANGE_Q, RANGE_ALPHA, RANGE_BETA, RANGE_RHO
        )
        all_hyperparams.append(hyperparams)
        hyperparams["Q"], hyperparams["RHO"] = 0, 1
        all_hyperparams.append(hyperparams)
    results = []
    for hyperparams in all_hyperparams:
        vrp = VRP(n, k, q, duration, load, hyperparams)
        best_iter, best_vrp_route_cost, best_vrp_route = vrp.solve()
        if best_vrp_route is not None:
            results.append(
                (best_vrp_route_cost, best_iter, best_vrp_route, hyperparams)
            )
    results.sort(key=lambda x: x[0])
    time_end = datetime.datetime.now()
    for result_idx, result in reversed(list(enumerate(results[:n_best_hyperparamas]))):
        best_vrp_route_cost, best_iter, best_vrp_route, hyperparams = result
        print_sol_1(
            result_idx,
            best_vrp_route_cost,
            best_iter,
            best_vrp_route,
            hyperparams,
            print_route=True,
        )
    print(f"\nTime elapsed = {time_end-time_start}")


if __name__ == "__main__":
    run()
