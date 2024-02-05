import math
import random
import numpy as np
from time import time

INF = 999999
LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_DEPOT_TIME_INIT = 30  # not used
UNLOADING_DEPOT_TIME_PER_UNIT = 10  # not used
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def step_duration(duration_matrix: list, current_node: int, next_node: int, depart_at: int):
    '''Returns the travel time from current_node to next_node.'''
    max_hour = duration_matrix.shape[2] - 1
    current_hour = min(int(depart_at / (60 * 60)), max_hour)
    # current_hour = 0
    return duration_matrix[current_node][next_node][current_hour]


def resupply_time(duration_matrix: list, customer_demands: list, vehicle_capacity: int, plan: list):

    # Determine the first cycle in the given plan
    cycle_end = plan.index(0) if 0 in plan else len(plan)
    cycle = plan[:cycle_end]

    # Return zero resupply time for empty tours
    if len(cycle) == 0:
        return 0

    # Calculate and return the time needed for resupply
    supply_need = sum((customer_demands[node] for node in cycle))
    supply_time = LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * supply_need

    return supply_time if supply_need <= vehicle_capacity else INF


def plan_duration(duration_matrix: list, customer_demands: list, vehicle_capacity: int, plan: list):

    current_node = 0  # Current node index, starting at warehouse
    current_time = 0  # Current seconds since the start of the plan
    current_load = vehicle_capacity  # Current load of the vehicle

    # Load supplies from warehouse at day start
    current_time = resupply_time(
        duration_matrix, customer_demands, vehicle_capacity, plan)

    for next_node_idx, next_node in enumerate(plan + [0]):
        customer_demand = customer_demands[next_node]
        arrival_time = current_time + \
            step_duration(duration_matrix, current_node,
                          next_node, current_time)

        # Resupply if arriving at warehouse
        if next_node == 0:
            current_load = vehicle_capacity
            finish_time = arrival_time + \
                resupply_time(duration_matrix, customer_demands,
                              vehicle_capacity, plan[next_node_idx + 1:])
        else:
            unload_time = UNLOADING_CUSTOMER_TIME_INIT + \
                UNLOADING_CUSTOMER_TIME_PER_UNIT * customer_demand
            finish_time = arrival_time + unload_time
            # Return infinity if infeasible action
            if current_load < customer_demand:
                return INF

        current_load = current_load - customer_demand
        current_time = finish_time
        current_node = next_node

        # Terminate early if infeasible
        if current_time >= INF:
            return INF

    return current_time


def solution_cost_sum(duration_matrix: list, customer_demands: list, vehicle_capacity: int, solution: list):
    return sum((plan_duration(duration_matrix, customer_demands, vehicle_capacity, plan) for plan in solution))


def solution_cost_max(duration_matrix: list, customer_demands: list, vehicle_capacity: int, solution: list):
    return max((plan_duration(duration_matrix, customer_demands, vehicle_capacity, plan) for plan in solution))


def solution_longest_plan(duration_matrix: list, customer_demands: list, vehicle_capacity: int, solution: list):
    return max((plan_duration(duration_matrix, customer_demands, vehicle_capacity, plan) for plan in solution))


def swap_intra(duration_matrix: list,
               customer_demands: list,
               vehicle_capacity: int,
               sol_current: list):

    # Select a random plan
    a = np.random.choice(range(len(sol_current)))
    plan = sol_current[a].copy()

    # Assert that the select plan is longer than 1 node
    if len(plan) < 2:
        return None

    # Select two node indexes uniformly random
    i, j = np.random.choice(range(len(plan)), size=2, replace=False)

    # Swap the selected nodes inside the plan
    plan[i], plan[j] = plan[j], plan[i]

    # Calculate the cost

    new_solution = sol_current.copy()
    new_solution[a] = plan
    new_cost = solution_cost_max(
        duration_matrix, customer_demands, vehicle_capacity, new_solution)

    return new_cost, new_solution


def swap_inter(duration_matrix: list,
               customer_demands: list,
               vehicle_capacity: int,
               sol_current: list,
               move=False):

    # Select a random plan idx with probability *directly* proportional to total duration
    a, b = np.random.choice(range(len(sol_current)), 2, replace=False)

    # Assert selected plans are different and not empty
    if a == b or len(sol_current[a]) == 0 or len(sol_current[b]) == 0:
        return None

    # Plan A is most likely expensive, plan B is most likely cheap
    plan_a = sol_current[a].copy()
    plan_b = sol_current[b].copy()

    # Select two node indexes uniformly random
    i = np.random.choice(range(len(plan_a)), replace=False)
    j = np.random.choice(range(len(plan_b)), replace=False)

    if move:
        # Move the selected node from plan a to plan b
        node = plan_a.pop(i)
        plan_b.insert(j, node)
    else:
        # Swap the selected nodes between routes
        plan_a[i], plan_b[j] = plan_b[j], plan_a[i]

    new_solution = sol_current.copy()
    new_solution[a], new_solution[b] = plan_a, plan_b
    new_cost = solution_cost_max(
        duration_matrix, customer_demands, vehicle_capacity, new_solution)

    return new_cost, new_solution


def move_inter(duration_matrix: list,
               customer_demands: list,
               vehicle_capacity: int,
               sol_current: list,
               move=False):

    # Select a random plan idx with probability *directly* proportional to total duration
    a, b = np.random.choice(range(len(sol_current)), 2, replace=False)

    # Assert selected plans are different and not empty
    if a == b or len(sol_current[a]) == 0 or len(sol_current[b]) == 0:
        return None

    # Plan A is most likely expensive, plan B is most likely cheap
    plan_a = sol_current[a].copy()
    plan_b = sol_current[b].copy()

    # Select two node indexes uniformly random
    i = np.random.choice(range(len(plan_a)), replace=False)
    j = np.random.choice(range(len(plan_b)), replace=False)

    # Move the selected node from plan a to plan b
    node = plan_a.pop(i)
    plan_b.insert(j, node)

    new_solution = sol_current.copy()
    new_solution[a], new_solution[b] = plan_a, plan_b
    new_cost = solution_cost_max(
        duration_matrix, customer_demands, vehicle_capacity, new_solution)

    return new_cost, new_solution


def generate_random_initial_solution(customer_count: int, vehicle_count: int, max_cycles: int, ignored_customers=[]):
    customer_idxs = list(range(1, customer_count + 1))
    customer_idxs = [
        idx for idx in customer_idxs if idx not in ignored_customers]
    random.shuffle(customer_idxs)
    solution = [list(plan) for plan in np.array_split(
        np.array(customer_idxs), vehicle_count)]
    for plan in solution:
        plan += [0] * (max_cycles - 1)
        random.shuffle(plan)
    return solution


def insert_resupply_runs(plan: list, customer_demands, vehicle_capacity, min_cycles: int):
    current_node = 0
    current_load = vehicle_capacity
    generated_plan = []

    for next_node in plan:
        customer_demand = customer_demands[next_node]

        if customer_demand <= current_load:
            generated_plan.append(next_node)
            current_load -= customer_demand
        else:
            generated_plan.append(0)
            generated_plan.append(next_node)
            current_load = vehicle_capacity

    missing_zeros = max(0, (min_cycles - 1) - generated_plan.count(0))
    if missing_zeros:
        generated_plan += [0] * missing_zeros

    return generated_plan


def anneal(duration_matrix: list,
           customer_demands: list,
           vehicle_capacity: int,
           initial_solution: list,
           initial_temperature: int,
           cooling_factor: float,
           step_length: int,
           terminate_after: int,
           trace_progress=True,
           icon=None,
           ignored_customers=[]):

    # Start timer
    time_start = time()

    # Initialize solutions
    sol_optimal = initial_solution.copy()
    sol_current = initial_solution.copy()
    cost_optimal = solution_cost_max(
        duration_matrix, customer_demands, vehicle_capacity, sol_optimal)
    cost_current = cost_optimal

    # Initialize variables
    temperature = initial_temperature
    total_iterations = 0

    # Initialize tracers
    tracer_bests = []
    tracer_costs = []
    tracer_temps = []

    # Main simulated annealing loop
    while total_iterations < terminate_after:

        for _ in range(step_length):
            total_iterations += 1

            if trace_progress:
                tracer_temps.append(temperature)
                tracer_costs.append(cost_current)
                tracer_bests.append(cost_optimal)

            experiments = sorted([proposal for proposal in [
                swap_intra(duration_matrix, customer_demands,
                           vehicle_capacity, sol_current),
                swap_inter(duration_matrix, customer_demands,
                           vehicle_capacity, sol_current),
                move_inter(duration_matrix, customer_demands,
                           vehicle_capacity, sol_current)
            ] if proposal is not None])

            if len(experiments) == 0:
                continue

            cost_new, sol_new = experiments[0]
            delta = cost_new - cost_current

            # Update the current solution if improved
            if delta <= 0:
                sol_current = sol_new
                cost_current = cost_new

                # Update the optimal solution if improved
                if cost_new < cost_optimal:
                    sol_optimal = sol_new.copy()  # must be a copy!
                    cost_optimal = cost_new
                    continue

            # Accept the new solution without improvement if lucky
            elif random.uniform(0, 1) < math.exp(-delta / temperature):
                sol_current = sol_new
                cost_current = cost_new

        # Decrease temperature after
        temperature *= cooling_factor

    if trace_progress:
        tracer_temps.append(temperature)
        tracer_costs.append(cost_current)
        tracer_bests.append(cost_optimal)

    # Calculate stats about the solution
    exec_time = time() - time_start
    sol_sum = int(solution_cost_sum(duration_matrix,
                  customer_demands, vehicle_capacity, sol_optimal))
    sol_max = int(solution_cost_max(duration_matrix,
                  customer_demands, vehicle_capacity, sol_optimal))

    return {'plans': sol_optimal, 'sol_sum': sol_sum, 'sol_max': sol_max, 'exec_time': exec_time}, \
           {'costs': tracer_costs, 'bests': tracer_bests, 'temps': tracer_temps}


def solve(durations: list,
          locations: list,
          customer_count: int,
          vehicle_count: int,
          vehicle_capacity: int,
          max_cycles: int,
          initial_temperature: int,
          cooling_factor: float,
          step_length: int,
          terminate_after: int,
          repeat_annealing: int,
          ignored_customers=[]):

    # Prepare parameters for Simulated Annealing
    N = customer_count
    duration_matrix = durations[:N+1]
    customer_demands = [location['demand'] for location in locations][:N+1]

    # Initialize results for each repeated SA call
    best_score = INF + 1
    best_result = None

    for _ in range(repeat_annealing):

        initial_solution = generate_random_initial_solution(
            customer_count, vehicle_count, max_cycles, ignored_customers)

        result = anneal(duration_matrix,
                        customer_demands,
                        vehicle_capacity,
                        initial_solution,
                        initial_temperature,
                        cooling_factor,
                        step_length,
                        terminate_after,
                        trace_progress=False,
                        icon=None)

        if result["sol_max"] < best_score:
            best_result = result
            best_score = result["sol_max"]

    # Result found here

    # Adds warehouse to the begin and end of a plans
    def add_begin_and_end(solution):
        return [[0] + plan + [0] for plan in solution]

    # Removes empty vehicle plans from the solution
    def remove_empty_plans(solution):
        return [(idx, plan) for idx, plan in enumerate(solution) if any(plan)]

    # Removes consequent warehouse visits from a tour
    def remove_trivial_visits(nodes):
        tour = [nodes[0]]
        current_node = nodes[0]
        for next_node in nodes[1:]:
            if current_node == 0 and next_node == 0:
                continue
            tour.append(next_node)
            current_node = next_node
        return tour

    def map_arrival_times(start_time, nodes):
        current_time = start_time
        current_node = nodes[0]
        result = [{
            'lat': locations[current_node]['lat'],
            'lng': locations[current_node]['lng'],
            'arrivalTime': current_time
        }]
        for next_node in nodes[1:]:
            duration = step_duration(
                duration_matrix, current_node, next_node, depart_at=current_time)
            arrival_time = current_time + duration
            result.append({
                'lat': locations[next_node]['lat'],
                'lng': locations[next_node]['lng'],
                'arrivalTime': arrival_time
            })
            current_node = next_node
            current_time = arrival_time
        return result

    def standardize_solution(solution):
        solution = add_begin_and_end(solution)
        solution = remove_empty_plans(solution)
        solution = [(idx, remove_trivial_visits(plan))
                    for idx, plan in solution]
        solution = [{
            'capacity': vehicle_capacity,
            'tours': map_arrival_times(0, plan)} for idx, plan in solution]
        return solution

    if best_result is None:
        return {}

    return {
        "durationMax": best_result['sol_max'],
        "durationSum": best_result['sol_sum'],
        "vehicles": standardize_solution(best_result['plans'])
    }
