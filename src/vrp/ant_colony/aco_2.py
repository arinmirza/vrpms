import datetime
import random
from typing import Any, Dict, List, Optional, Tuple

from src.vrp.ant_colony.aco import ACO_VRP
from src.vrp.ant_colony.aco_helper import get_hyperparams, print_sol_2
from src.utilities.vrp_helper import get_based_and_load_data, get_google_and_load_data

N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 60  # hour = 60 minutes
TOTAL_TIME = N_TIME_ZONES * TIME_UNITS
IGNORE_LONG_TRIP = True

INPUT_FOLDER_PATH = "../../../data/google_api/dynamic/float"
INPUT_FILE_NAME_PREFIX = "dynamic_duration_float"
INPUT_FILES_TIME = [f"{INPUT_FOLDER_PATH}/{INPUT_FILE_NAME_PREFIX}_{hour}.txt" for hour in range(N_TIME_ZONES)]

N_SUB_ITERATIONS = 5
RANGE_N_ITERATIONS = (100, 1000)
RANGE_Q = (1, 1000)
RANGE_ALPHA = (2, 5)
RANGE_BETA = (2, 5)
RANGE_RHO = (0.8, 1)

INF = float("inf")


class ACO_VRP_2(ACO_VRP):
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
        super().__init__(n, m, init_capacity, duration, load, hyperparams)

    def update_pheromone(self, ant_routes: List[List[int]], ant_route_costs: List[float]) -> None:
        """
        Updates pheromone values to be used while selecting next location to visit. For more information on update:
            https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

        :param ant_routes: Completed VRP tour, including visited locations in order
        :param ant_route_costs: Costs for each ant
        """
        for i in range(self.n):
            for j in range(self.n):
                self.pheromone[i][j] *= self.RHO
        n_ants = len(ant_route_costs)
        for i in range(n_ants):
            ant_route = ant_routes[i]
            ant_route_cost = ant_route_costs[i]
            ant_route_len = len(ant_route)
            for idx in range(ant_route_len):
                u, v = ant_route[idx - 1], ant_route[idx]
                self.pheromone[u][v] += self.Q / ant_route_cost

    def solve(self) -> Tuple[int, float, List[int]]:
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
            for _ in range(N_SUB_ITERATIONS):
                visited = [False for _ in range(self.n)]
                visited[0] = True
                fail = False
                vrp_route = [0]
                vrp_route_cost = 0
                n_tours = 0
                capacity = self.init_capacity
                # Check if constraint based on the number of cycles satisfied
                while n_tours < self.m:
                    hour = int(vrp_route_cost / TIME_UNITS)
                    # Check if exceeds the time limit
                    if hour >= N_TIME_ZONES:
                        if IGNORE_LONG_TRIP:
                            fail = True
                            break
                        else:
                            hour = N_TIME_ZONES - 1
                    ant_node = vrp_route[-1]
                    nodes = []
                    # Fetch unvisited nodes to visit next
                    for node in range(self.n):
                        if not visited[node]:
                            nodes.append(node)
                    # Get the next node based on pheromones
                    next_node = self.get_next_node(nodes, ant_node, hour) if nodes else 0
                    if next_node != 0 and capacity >= self.load[next_node]:
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
                        capacity = self.init_capacity
                        vrp_route_cost += self.duration[ant_node][next_node][hour]
                # Check if exceeds the time limit
                if not fail:
                    if vrp_route_cost > TOTAL_TIME or self.check_unvisited_node_exists(visited):
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
        return best_iter, best_of_best_cost, best_of_best_route


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
        duration, load = get_google_and_load_data(INPUT_FILES_TIME, input_file_load, n)
    else:
        duration, load = get_based_and_load_data(input_file_load, n, per_km_time)
    time_start = datetime.datetime.now()
    all_hyperparams = []
    for _ in range(n_hyperparams // 2):
        hyperparams = get_hyperparams(RANGE_N_ITERATIONS, RANGE_Q, RANGE_ALPHA, RANGE_BETA, RANGE_RHO)
        all_hyperparams.append(hyperparams)
        hyperparams["Q"], hyperparams["RHO"] = 0, 1
        all_hyperparams.append(hyperparams)
    results = []
    for hyperparams in all_hyperparams:
        vrp = ACO_VRP_2(n, k, q, duration, load, hyperparams)
        best_iter, best_vrp_route_cost, best_vrp_route = vrp.solve()
        if best_vrp_route is not None:
            results.append((best_vrp_route_cost, best_iter, best_vrp_route, hyperparams))
    results.sort(key=lambda x: x[0])
    time_end = datetime.datetime.now()
    for result_idx, result in reversed(list(enumerate(results[:n_best_hyperparamas]))):
        best_vrp_route_cost, best_iter, best_vrp_route, hyperparams = result
        print_sol_2(
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
