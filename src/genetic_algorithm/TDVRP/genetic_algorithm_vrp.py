# Genetic Algorithm TDVRP
# Yusuf Serdar Degerli
# TUM MSc Informatics & Management Student
# Interdisciplinary Project with SAP

# Imports: General
import copy
from datetime import datetime
from iteration_utilities import random_permutation
import math
import random
from typing import List, Optional, Tuple, Dict
from collections import defaultdict
from itertools import groupby

# Imports: Libraries for Parallel Processing
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

# Imports: Project Files to be Imported
from src.utilities.vehicles_priority_queue.vehicles_pq import VehiclesPQ

# PARAMETERS
MIN_ENTRY_COUNT = 25  # used for deciding on making or skipping the selection & replacement step
INF = float("inf")
N_TIME_SLICES = 12
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60 minutes
DEPOT = 0


#######################################################################################################################
#######################################################################################################################
# GENETIC ALGORITHM LOGIC


def random_selection(permutations, sel_count, already_selected=[]):
    """
    Randomly selects 'sel_count' many permutations and starts the process with the permutations available in
    'already selected' list

    :param permutations: all available permutations
    :param sel_count: number of permutations to be selected
    :param already_selected: previously selected permutations
    """
    # select 'sel_count' many permutations in a random fashion
    selection_indices = []
    while len(already_selected) < sel_count:
        rand_index = random.randint(0, len(permutations) - 1)
        while rand_index in selection_indices:
            rand_index = random.randint(0, len(permutations) - 1)

        already_selected.append(permutations[rand_index])
        selection_indices.append(rand_index)

    return already_selected


def reverse_insert_probability_list(permutations, probability_list, inf_start_at_index):
    """
    Reverses the probability ranges to be matched with each permutation available
    This allows the permutations with smaller duration to get a bigger portion
    in the fitness proportional selection

    :param permutations: all available permutations
    :param probability_list: duration based fitness intervals
    :param inf_start_at_index: indicates the index at which the infeasible permutations start getting listed in
                                the 'permutations' list
    """

    # the fitness and total cost are inversely related
    # permutations with shorter duration will get higher fitness value

    # divide the probability list into two depending on the inf total duration values
    probability_list_non_inf_values = probability_list[:inf_start_at_index]
    probability_list_inf_values = probability_list[inf_start_at_index:]

    # reverse the duration based probability list and assign bigger portions for the permutations with lower duration
    probability_list_non_inf_values.reverse()
    current_fitness_level = 0
    for index in range(0, len(probability_list_non_inf_values)):

        if not len(permutations[index]) >= 7:

            permutations[index].append(
                [current_fitness_level, current_fitness_level + probability_list_non_inf_values[index]]
            )
            current_fitness_level = current_fitness_level + probability_list_non_inf_values[index]

        else:
            permutations[index][6] = [
                current_fitness_level,
                current_fitness_level + probability_list_non_inf_values[index],
            ]
            current_fitness_level = current_fitness_level + probability_list_non_inf_values[index]

    # fills in the rest of the probability range values for the remaining permutations in the list
    count = 0
    for index in range(len(probability_list_non_inf_values), len(permutations)):

        if not len(permutations[index]) >= 7:
            permutations[index].append(
                [current_fitness_level, current_fitness_level + probability_list_inf_values[count]]
            )
            current_fitness_level = current_fitness_level + probability_list_inf_values[count]

        else:
            permutations[index][6] = [current_fitness_level, current_fitness_level + probability_list_inf_values[count]]
            current_fitness_level = current_fitness_level + probability_list_inf_values[count]

        count = count + 1

    return permutations


def calculate_fitness_level(remaining_permutations):
    """
     Based on the previously calculated duration information, calculate the fitness level of each permutation

    :param remaining_permutations: all available permutations
    """
    # print("SELECTION: Calculating fitness level...")

    sorted(remaining_permutations, key=lambda x: x[2], reverse=False)
    shortest_duration = remaining_permutations[0][2]
    total_sum = 0

    for elem in remaining_permutations:
        # if the permutation is not infeasible then add the total duration to the total sum
        if elem[2] != math.inf:
            total_sum = total_sum + elem[2]
        # if the permutation is infeasible then add the shortest duration of the permutation list as the
        # total duration of the infeasible solution so that the fitness value distribution would be balanced
        else:
            total_sum = total_sum + shortest_duration

    probability_list = []
    inf_starts_at_index = 0

    # the index at which the infeasible solutions start is found and stored for it to be used in the reversion method
    for index in range(0, len(remaining_permutations)):

        # find the non-reversed fitness level of each permutation
        if remaining_permutations[index][2] != math.inf:
            fitness_level = remaining_permutations[index][2] / total_sum
        else:
            fitness_level = (shortest_duration) / total_sum

            if inf_starts_at_index == 0:  # if it has been already changed then do not change it again
                inf_starts_at_index = index

        # store the non-reversed fitness level
        probability_list.append(fitness_level)

    # find the original/adjusted/reversed fitness levels
    remaining_permutations = reverse_insert_probability_list(
        remaining_permutations, probability_list, inf_starts_at_index
    )

    return remaining_permutations


def select_based_on_fitness_proportional(permutations):
    """
     Select a predefined number of permutations from the given permutations list

    :param permutations: all available permutations
    """

    start = datetime.now()
    mode = "FITNESS"
    selection_len = int(len(permutations) * 5 / 8)
    selected = []

    # continue fitness proportional selection until the selection length is reached
    while len(selected) < selection_len:

        end = datetime.now()

        if (end - start).seconds >= 0.5:
            # current implementation of the fitness proportional method might take some time
            # current time limit is 10 seconds
            # if the threshold is exceeded than selection mode is switched to RANDOM selection
            mode = "RANDOM"
            break

        else:  # time limit has not reached, continue fitness proportional selection
            # generate random number between 0 and 1
            rand = random.uniform(0, 1)

            # find the permutation which has this value in its own fitness range
            for index in range(0, len(permutations)):
                elem = permutations[index]
                if elem[6][0] <= rand <= elem[6][1] and elem[1]:
                    selected.append(elem)
                    break

    if mode == "RANDOM":
        return random_selection(permutations=permutations, sel_count=selection_len, already_selected=selected)

    return selected


# REPLACEMENT


def deterministic_best_n_replacement(permutations, n=-1):
    """
    Sort the permutations based on duration and return the best n
    If n is not specified simply get the first half of the list

    :param permutations: all available permutations
    :param n: number of items to be selected
    """

    if n != -1:
        replacement_count = n
    else:
        replacement_count = int(len(permutations) / 2)

    return sorted(permutations, key=lambda x: x[2], reverse=False)[:replacement_count]


# REPRODUCTION


def swap_mutation(permutations, VST, dist_data, M, Q, demand_dict):
    """
    Select two random indices and swap these indices
    If the mutated permutation has a longer duration than the previous permutation, simply revert the swap
    If the mutated permutation has a smaller duration than the previous permutation, keep the mutation

    :param permutations: all available permutations
    """

    DIST_DATA = dist_data
    vehicles_start_times = VST

    for index in range(0, len(permutations)):

        single_perm = permutations[index]

        count = 0
        while count < 10:  # threshold for the number of SWAP mutation to be applied, for now it is 10
            # select two random positions
            # indices 0 and -1 are not included
            pos1 = random.randint(1, len(single_perm[0]) - 2)
            pos2 = random.randint(1, len(single_perm[0]) - 2)

            # if two positions are not equal and none of the positions equal to DEPOT
            if pos1 != pos2 and single_perm[0][pos1] != DEPOT and single_perm[0][pos2] != DEPOT:

                # swap the indices
                temp = single_perm[0][pos1]
                single_perm[0][pos1] = single_perm[0][pos2]
                single_perm[0][pos2] = temp
                # calculate the new duration
                a, b, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
                    permutation=single_perm[0],
                    VST=vehicles_start_times,
                    dist_data=DIST_DATA,
                    M=M,
                    Q=Q,
                    demand_dict=demand_dict,
                )
                # if the new duration is shorter than the previous one keep it
                if a < single_perm[2]:
                    single_perm[2], single_perm[1] = a, b
                    single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times

                # if the new duration is longer than the previous one revert the changes
                else:
                    temp = single_perm[0][pos1]
                    single_perm[0][pos1] = single_perm[0][pos2]
                    single_perm[0][pos2] = temp
            count = count + 1
    return permutations


def scramble_mutation(permutations, VST, dist_data, M, Q, demand_dict):
    """
    Select two random indices
    Shuffle everything that stays between these two randomly selected indices

    :param permutations: all available permutations
    """

    DIST_DATA = dist_data
    vehicles_start_times = VST

    for index in range(0, len(permutations)):
        # get the current permutation
        single_perm = permutations[index]

        count = 0
        while count < 1:  # threshold for the number of SCRAMBLE mutation to be applied, for now it is 1
            # select two random positions
            # indices 0 and -1 are not included
            pos1 = random.randint(1, len(single_perm[0]) - 2)
            pos2 = random.randint(1, len(single_perm[0]) - 2)

            while pos1 == pos2:
                pos1 = random.randint(1, len(single_perm[0]) - 2)
                pos2 = random.randint(1, len(single_perm[0]) - 2)

            # save the lower and upper bounds as a pair
            bound = (pos1, pos2) if pos1 < pos2 else (pos2, pos1)

            if pos1 != pos2:
                max_try = 3
                while True:

                    # get the part before the selected portion
                    lower_part = single_perm[0][0 : bound[0]]
                    # get the part after the selected portion
                    upper_part = single_perm[0][bound[1] + 1 :]
                    # get the portion to be reversed
                    subpart = single_perm[0][bound[0] : bound[1] + 1]
                    # scramble the related portion
                    random.shuffle(subpart)

                    old_perm = single_perm[0]
                    # construct the permutation with the reversed portion
                    new_perm = lower_part + subpart + upper_part

                    single_perm[0] = new_perm

                    if check_neighbor(single_perm[0], source="scramble"):
                        break

                    else:

                        while pos1 == pos2:
                            pos1 = random.randint(1, len(single_perm[0]) - 2)
                            pos2 = random.randint(1, len(single_perm[0]) - 2)

                        # save the lower and upper bounds as a pair
                        bound = (pos1, pos2) if pos1 < pos2 else (pos2, pos1)
                        single_perm[0] = old_perm
                        max_try = max_try - 1

                        if max_try == 0:
                            break

                # calculate new duration and save
                a, b, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
                    single_perm[0], VST=vehicles_start_times, dist_data=DIST_DATA, M=M, Q=Q, demand_dict=demand_dict
                )
                # a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times
                # single_perm.append(route_sum_time)
                # single_perm.append(vehicle_routes)
                # single_perm.append(vehicle_times)

            count = count + 1
    return permutations


def inversion_mutation(permutations, VST, dist_data, M, Q, demand_dict):
    """
    Select two random indices
    Reverse everything that stays between these two randomly selected indices

    :param permutations: all available permutations
    """

    DIST_DATA = dist_data
    vehicles_start_times = VST

    for index in range(0, len(permutations)):
        # get the current permutation
        single_perm = permutations[index]

        count = 0
        while count < 1:  # threshold for the number of inversion mutation to be applied, for now it is 1
            # select two random positions
            # indices 0 and -1 are not included
            pos1 = random.randint(1, len(single_perm[0]) - 2)
            pos2 = random.randint(1, len(single_perm[0]) - 2)

            # save the lower and upper bounds as a pair
            bound = (pos1, pos2) if pos1 < pos2 else (pos2, pos1)

            if pos1 != pos2:

                # get the part before the selected portion
                lower_part = single_perm[0][0 : bound[0]]
                # get the part after the selected portion
                upper_part = single_perm[0][bound[1] + 1 :]
                # get the portion to be reversed
                subpart = single_perm[0][bound[0] : bound[1] + 1]
                # reverse the related portion
                list.reverse(subpart)
                # construct the permutation with the reversed portion
                single_perm[0] = lower_part + subpart + upper_part

                # calculate new duration and save
                a, b, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
                    single_perm[0], VST=vehicles_start_times, dist_data=DIST_DATA, M=M, Q=Q, demand_dict=demand_dict
                )
                # a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times
                # single_perm.append(route_sum_time)
                # single_perm.append(vehicle_routes)
                # single_perm.append(vehicle_times)
            count = count + 1

    return permutations


def genetic_algorithm(population, N, M, k, q, W, duration, ist, demand_dict):
    """
    Apply Mutation and Selection & Replacement operations
    based on the random probabilities generated

    :param population: all available permutations
    """

    N = N  # number of shops to be considered
    K = k
    Q = q
    M = M
    DEPOT = W
    DIST_DATA = duration
    # LOAD = demand_in
    vehicles_start_times = ist

    new_population = None  # empty variable for the output population

    # assigned probabilities for each mutation option
    SWAP_MUTATION_PROB = (0, 0.33)
    INVERSION_MUTATION_PROB = (0.33, 0.66)
    SCRAMBLE_MUTATION_PROB = (0.66, 1)

    # assigned probabilities for each selection & replacement option
    SELECTION_PROB = (0, 0)  # de-activated
    REPLACEMENT_PROB = (0, 0.5)
    RANDOM_SELECTION_PROB = (0.5, 0.75)
    NO_SELECTION_REPLACEMENT_PROB = (0.75, 1)

    # generate random probabilities
    rand_phase_1 = random.uniform(0, 1)
    rand_phase_2 = random.uniform(0, 1)

    # PHASE 1 MUTATION
    updated_population = population
    if SWAP_MUTATION_PROB[0] <= rand_phase_1 <= SWAP_MUTATION_PROB[1]:
        # print("REPRODUCTION: applying swap mutation...")
        updated_population = swap_mutation(
            population, VST=vehicles_start_times, dist_data=DIST_DATA, M=M, Q=Q, demand_dict=demand_dict
        )
    elif INVERSION_MUTATION_PROB[0] <= rand_phase_1 <= INVERSION_MUTATION_PROB[1]:
        # print("REPRODUCTION: applying inversion mutation...")
        updated_population = inversion_mutation(
            population, VST=vehicles_start_times, dist_data=DIST_DATA, M=M, Q=Q, demand_dict=demand_dict
        )
    elif SCRAMBLE_MUTATION_PROB[0] <= rand_phase_1 <= SCRAMBLE_MUTATION_PROB[1]:
        # print("REPRODUCTION: applying scramble mutation...")
        updated_population = scramble_mutation(
            population, VST=vehicles_start_times, dist_data=DIST_DATA, M=M, Q=Q, demand_dict=demand_dict
        )

    # PHASE 2 SELECTION & REPLACEMENT
    if len(updated_population) > MIN_ENTRY_COUNT:
        # if the number of permutations available is less than MIN_ENTRY_COUNT do not apply selection & replacement
        if SELECTION_PROB[0] <= rand_phase_2 <= SELECTION_PROB[1]:
            # print("SELECTION & REPLACEMENT: applying selection...")
            # first calculate the fitness value of all permutations
            population_with_fitness = calculate_fitness_level(updated_population)
            # then select permutations based on fitness value
            new_population = select_based_on_fitness_proportional(population_with_fitness)

            pass
            # post process the permutations
            # for elem in new_population:
            #    if len(elem) > 4:
            #        del elem[4]

        elif REPLACEMENT_PROB[0] <= rand_phase_2 <= REPLACEMENT_PROB[1]:
            # print("SELECTION & REPLACEMENT: applying replacement...")
            new_population = deterministic_best_n_replacement(updated_population)

        elif RANDOM_SELECTION_PROB[0] <= rand_phase_2 <= RANDOM_SELECTION_PROB[1]:
            # print("SELECTION & REPLACEMENT: applying random selection...")
            new_population = random_selection(
                updated_population, (len(updated_population) * 5 / 8), already_selected=[]
            )

        elif NO_SELECTION_REPLACEMENT_PROB[0] <= rand_phase_2 <= NO_SELECTION_REPLACEMENT_PROB[1]:
            # print("SELECTION & REPLACEMENT: no operation...")
            new_population = updated_population
    else:
        new_population = updated_population

    return new_population


#######################################################################################################################
#######################################################################################################################
# DURATION CALCULATION AND RUN

LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10


def helper(
    q: int,
    m: int,
    ignore_long_trip: bool,
    cycles: List[List[int]],
    duration: List[List[List[float]]],
    vehicles_start_times: List[float],
    demand_dict: Dict[int, int],
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given list of cycles

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param ignore_long_trip: Flag to ignore long trips
    :param cycles: The cycles to be assigned where one cycle is demonstrated as [DEPOT, c_i, ..., c_j, DEPOT]
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """

    # Initialize vehicle id to cycles and times mapping
    vehicle_routes = defaultdict(list)

    # Initialize the PQ of vehicles (drivers) with given (expected) start time
    vehicles_pq = VehiclesPQ(vehicles_start_times)

    # Cycle: [DEPOT, customer_1, customer_2, ..., customer_k, DEPOT]
    # Cycles: [cycle_1, cycle_2, ...]
    for cycle in cycles:
        # Get the vehicle (driver) with the earliest available time
        vehicle_t, vehicle_id = vehicles_pq.get_vehicle()
        last_node = DEPOT
        curr_capacity = q
        total_load = 0
        for customer in cycle:
            total_load += demand_dict[customer]
        if total_load > 0:
            vehicle_t += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load
        # Go over each edge in the cycle
        for node in cycle[1:]:
            # Update capacity and check if it exceeds the initial capacity
            curr_capacity -= demand_dict[node]
            if curr_capacity < 0:
                return INF, INF, None, None
            # Determine the hour and check if it exceeds the number of time zones (based on ignore_long_trip)
            hour = int(vehicle_t / TIME_UNITS)
            if not ignore_long_trip:
                hour = min(hour, N_TIME_ZONES - 1)
            if hour >= N_TIME_ZONES:
                return INF, INF, None, None
            # Update time and node
            vehicle_t += duration[last_node][node][hour]
            if node != DEPOT:
                vehicle_t += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * demand_dict[node]
            last_node = node
        # Update PQ with the chosen vehicle and updated time
        vehicles_pq.put_vehicle(vehicle_t, vehicle_id)
        vehicle_routes[vehicle_id].append(cycle)

    # Pull elements from PQ and update vehicle id to cycles and times mapping
    # route_max_time: max of duration among all vehicles (drivers)
    # route_sum_time: sum of duration of all vehicles (drivers)
    route_max_time, route_sum_time, vehicle_times = vehicles_pq.get_route_and_vehicle_times()

    # Check if it exceeds the number of time zones (based on ignore_long_trip)
    if ignore_long_trip and route_max_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, INF, None, None

    return route_max_time, route_sum_time, vehicle_routes, vehicle_times


def calculate_duration_perm(
    perm: List[int],
    duration: List[List[List[float]]],
    vehicles_start_times: Optional[List[float]],
    q: int,
    m: int,
    demand_dict: Dict[int, int],
    ignore_long_trip: bool = False,
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations for the latest driver, sum of the durations of each driver and
        the routes for each driver, given permutation of nodes

    :param q: Capacity of vehicle
    :param m: Max number of vehicles
    :param ignore_long_trip: Flag to ignore long trips
    :param perm: The locations to visit in order
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all assumed
        as zero.
    :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver, the
        routes for each driver and the travel duration for each driver
    """
    perm = list(perm)
    perm.append(DEPOT)

    cycles = []
    last_cycle = []
    for node in perm:
        if node == DEPOT:
            if len(last_cycle) > 0:
                cycle = [DEPOT]
                cycle.extend(last_cycle)
                cycle.append(DEPOT)
                cycles.append(cycle)
                last_cycle = []
        else:
            last_cycle.append(node)

    return helper(
        q=q,
        m=m,
        ignore_long_trip=ignore_long_trip,
        cycles=cycles,
        duration=duration,
        vehicles_start_times=vehicles_start_times,
        demand_dict=demand_dict,
    )


def calculate_duration(permutation, VST, dist_data, M, Q, demand_dict):

    route = []
    for elem in permutation:
        node = elem
        route.append(node)

    if VST is None:
        VST = [0 for _ in range(M)]
    else:
        assert len(VST) == M, f"Size of the vehicles_start_times should be {M}"

    route_max_time, route_sum_time, vehicle_routes, vehicle_times = calculate_duration_perm(
        q=Q, m=M, perm=route, duration=dist_data, vehicles_start_times=VST, demand_dict=demand_dict
    )

    return route_max_time, route, route_sum_time, vehicle_routes, vehicle_times


def check_neighbor(perm, source="def"):
    """
    Randomly generated permutations can not have two DEPOT nodes side by side.
    In that case shift places.
    This method returns if two DEPOT objects are neighbor to each other.
    """

    for i in range(1, len(perm)):
        if perm[i] == perm[i - 1] == DEPOT:
            return False

    if source == "def":
        if perm[0] == DEPOT or perm[-1] == DEPOT:
            return False

    return True


def intelligent_permutation(customer_list, k, q, rand_perm_count, depot=DEPOT):
    """
    Intelligent permutation method aims to generate feasible starting sequences
    In some solution spaces with a restricted k value, it might be hard for the random permutation generation model
    to generate sufficient number of feasible starting sequences
    """
    cl_copy = copy.deepcopy(customer_list)
    final_perms = []
    perm_basis = []

    current_cap = 0
    while len(final_perms) < rand_perm_count / 2:

        for elem in cl_copy:
            if current_cap < q:
                perm_basis.append(elem)

            elif current_cap == q:
                perm_basis.append(depot)
                perm_basis.append(elem)
                current_cap = 0

            current_cap = current_cap + 1

        current_cap = 0
        perm_basis.insert(0, DEPOT)
        perm_basis.append(DEPOT)
        final_perms.append(copy.deepcopy(perm_basis))
        random.shuffle(cl_copy)  # enables randomization of sequences for intelligent permutation technique
        perm_basis = []

    return final_perms


def ga(
    N,
    M,
    k,
    q,
    W,
    duration,
    demand,
    ist,
    customer_list,
    demand_dict,
    population_count=125,
    max_k=0,
    k_lower_limit=True,
    permutations=None,
):
    """
    Main method that controls the mode of the genetic algorithm
    If no input is given than it starts with population generation and runs genetic algorithm
    If 'permutations' list is given then skips population generation and runs genetic algorithm
    """

    # main method of the program
    # all threads run this method in parallel
    N = N  # number of shops to be considered
    K = k  # number of tours to be considered
    Q = q  # capacity of vehicles
    M = M  # vehicle count
    DEPOT = W  # DEPOT index
    DIST_DATA = duration  # duration data
    vehicles_start_times = ist  # vehicle start times
    intelligent_perm_generation_performed = False  # check for intelligent perm generation
    RANDOM_PERM_COUNT = population_count  # defines the population size

    # if the given input to this method is none, then a new population is generated from scratch
    if permutations is None:
        NODES_LIST = []
        NODES = []
        if len(customer_list) != 0:
            # there exists a user set customer list, use it directly
            NODES = copy.deepcopy(customer_list)
        else:
            # user set customer list does not exits, use N
            NODES.extend(range(1, N + 1))

        # there can be different number of tours in each permutation
        # the upper limit is K or K_max (K_max option is enabled if k_lower_limit is set to False)

        for _ in range(K - 1):
            NODES.append(DEPOT)

        NODES_LIST.append(NODES)

        # k_lower_limit is False
        # Thus, k upper limit will be defined by the user
        # If user did not specify the max_k -> simply user M*2
        if not k_lower_limit:

            if max_k == 0:
                max_k = M * 2

            for current_k in range(K + 1, max_k + 1):
                new_nodes_wo_k_limit = copy.deepcopy(customer_list)
                for _ in range(current_k - 1):
                    new_nodes_wo_k_limit.append(DEPOT)
                NODES_LIST.append(new_nodes_wo_k_limit)

        random_generated_perm = []

        while len(random_generated_perm) <= RANDOM_PERM_COUNT:
            for elem in NODES_LIST:

                # random permutation is generated
                random_perm = random_permutation(elem)
                random_perm = list(random_perm)

                # two DEPOT objects can not be neighbor to each other
                # while this is the case, generate a new random permutation
                # this process can be repeated up to 3 times
                check_count = 0
                while not check_neighbor(random_perm) and check_count < 3:
                    random_perm = random_permutation(elem)
                    random_perm = list(random_perm)
                    check_count = check_count + 1

                # DEPOT is added to the beginning and to the end
                random_perm.insert(0, DEPOT)
                random_perm.append(DEPOT)

                # duration is calculated
                total_dist, route, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
                    permutation=random_perm,
                    dist_data=DIST_DATA,
                    VST=vehicles_start_times,
                    M=M,
                    Q=Q,
                    demand_dict=demand_dict,
                )

                # constructed the tour information list
                random_perm_tuple = [random_perm, route, total_dist, route_sum_time, vehicle_routes, vehicle_times]

                random_generated_perm.append(random_perm_tuple)

        if (
            not intelligent_perm_generation_performed
            and len(list(filter(lambda y: y[2] == math.inf, random_generated_perm))) >= len(random_generated_perm) / 12
        ):

            # Intelligent permutation mode enabled
            # Remove half of the randomly generated sequences
            # Add intelligently generated randomized and feasible
            # starting sequences to the second half of the population set

            intelligent_perm_generation_performed = True
            intelligent_perms = intelligent_permutation(
                customer_list=customer_list, q=q, k=k, rand_perm_count=population_count
            )
            random_generated_perm = random_generated_perm[0 : len(random_generated_perm) // 2]
            for intelligent_perm in intelligent_perms:
                total_dist, route, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
                    permutation=intelligent_perm,
                    dist_data=DIST_DATA,
                    VST=vehicles_start_times,
                    M=M,
                    Q=Q,
                    demand_dict=demand_dict,
                )
                intelligent_perm_tuple = [
                    intelligent_perm,
                    route,
                    total_dist,
                    route_sum_time,
                    vehicle_routes,
                    vehicle_times,
                ]
                random_generated_perm.append(intelligent_perm_tuple)

        # sort the set based on duration of sequences (i.e. x[2])
        random_generated_perm = sorted(random_generated_perm, key=lambda x: x[2], reverse=False)

        # genetic algorithm code is called
        res = genetic_algorithm(
            population=random_generated_perm,
            N=N,
            M=M,
            k=K,
            q=Q,
            W=DEPOT,
            duration=DIST_DATA,
            ist=vehicles_start_times,
            demand_dict=demand_dict,
        )

        # results are sorted based on duration of sequences  (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    else:
        # prior permutations exist, do not generate new data and continue with the given input
        res = genetic_algorithm(
            population=permutations,
            N=N,
            M=M,
            k=K,
            q=Q,
            W=DEPOT,
            duration=DIST_DATA,
            ist=vehicles_start_times,
            demand_dict=demand_dict,
        )

        # results are sorted based on duration of sequences  (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    return res


def run(
    N,
    M,
    k,
    q,
    W,
    duration,
    demand_dict,
    ist,
    customer_list,
    multithreaded,
    max_k,
    k_lower_limit=True,
    population_count=125,
    iteration_count=48,
):

    N = N  # number of shops to be considered
    K = k  # number of tours to be considered
    Q = q  # capacity of the vehicles
    M = M  # number of vehicles
    DEPOT = W  # DEPOT index
    DIST_DATA = duration  # duration data
    vehicles_start_times = ist  # start times of the vehicles
    start_time = datetime.now()  # used for runtime calculation
    ITERATION_COUNT = iteration_count  # GA hyperparameter iteration number

    # should size of the customer list equals to 1
    # no need to perform GA
    if len(customer_list) == 1:
        one_node = copy.deepcopy(customer_list)
        one_node.append(DEPOT)
        one_node.insert(0, DEPOT)
        route_max_time, route, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(
            permutation=one_node, dist_data=DIST_DATA, VST=vehicles_start_times, M=M, Q=Q, demand_dict=demand_dict
        )

        return (route_max_time, route_sum_time, vehicle_routes, vehicle_times, str(0))

    # set the number of cores to be used
    if multithreaded:
        # get the number of available cores
        num_cores = int(multiprocessing.cpu_count())
    else:
        num_cores = 1

    # run num_cores many threads in parallel
    # at the beginning there exists no input for the ga method, permutations will be equal to None
    inputs = tqdm(num_cores * [1], disable=True)
    processed_list = Parallel(n_jobs=num_cores)(
        delayed(ga)(
            N=N,
            M=M,
            k=K,
            q=Q,
            W=DEPOT,
            duration=DIST_DATA,
            demand=demand_dict,
            ist=vehicles_start_times,
            permutations=None,
            customer_list=customer_list,
            demand_dict=demand_dict,
            k_lower_limit=k_lower_limit,
            max_k=max_k,
            population_count=population_count,
        )
        for i in inputs
    )

    iteration_count = 0
    best = []

    # first iteration phase starts
    while iteration_count < ITERATION_COUNT:

        inputs = tqdm(processed_list, disable=True)
        processed_list = Parallel(n_jobs=num_cores)(
            delayed(ga)(
                N=N,
                M=M,
                k=K,
                q=Q,
                W=DEPOT,
                duration=DIST_DATA,
                demand=demand_dict,
                ist=vehicles_start_times,
                permutations=i,
                demand_dict=demand_dict,
                customer_list=customer_list,
                k_lower_limit=k_lower_limit,
                max_k=max_k,
                population_count=population_count,
            )
            for i in inputs
        )

        for elem in processed_list:
            # sort the results based on duration of sequences  (i.e. x[2])
            elem = sorted(elem, key=lambda x: x[2], reverse=False)

            # save the best result of the current iteration
            best.append(copy.deepcopy(elem[0]))

        iteration_count = iteration_count + 1

        if (iteration_count % (ITERATION_COUNT / 3)) == 0 and iteration_count != ITERATION_COUNT:

            # Intermediary new population generation is enabled
            processed_list = Parallel(n_jobs=num_cores)(
                delayed(ga)(
                    N=N,
                    M=M,
                    k=K,
                    q=Q,
                    W=DEPOT,
                    duration=DIST_DATA,
                    demand=demand_dict,
                    ist=vehicles_start_times,
                    permutations=None,
                    demand_dict=demand_dict,
                    customer_list=customer_list,
                    k_lower_limit=k_lower_limit,
                    max_k=max_k,
                    population_count=population_count,
                )
                for i in inputs
            )

    # sort the results of the first iteration phase
    best_result_list = sorted(best, key=lambda x: x[2], reverse=False)

    best_route_max_time_r1 = best_result_list[0][2]
    best_route_sum_time_r1 = best_result_list[0][3]
    best_vehicle_routes_r1 = best_result_list[0][4]
    best_vehicle_times_r1 = best_result_list[0][5]

    if best_vehicle_times_r1 is None:
        print("FIRST ITERATION PHASE: No feasible solution")
    else:
        print(f"FIRST ITERATION PHASE: Best route max time: {best_route_max_time_r1}")
        print(f"FIRST ITERATION PHASE: Best route sum time: {best_route_sum_time_r1}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes_r1.items():
            print(f"FIRST ITERATION PHASE: Route of vehicle {vehicle_id}: {vehicle_cycles}")
        for vehicle_id, vehicle_time in best_vehicle_times_r1.items():
            print(f"FIRST ITERATION PHASE: Time of vehicle {vehicle_id}: {vehicle_time}")

    print("------------------------------ FIRST ITERATION PHASE IS COMPLETED ------------------------------")

    best = sorted(best, key=lambda x: x[2], reverse=False)
    iteration_count = 0
    all_equal_count = 0
    new_best = []

    def all_equal(iterable):
        # this method checks if the results of different threads are converging to the same point or not
        # returns a boolean answer
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

    # second iteration phase starts
    while iteration_count < ITERATION_COUNT / 4:

        inputs = tqdm(processed_list, disable=True)
        # the GA iterations will work on the best sequences achieved so far
        processed_list = Parallel(n_jobs=num_cores)(
            delayed(ga)(
                N=N,
                M=M,
                k=K,
                q=Q,
                W=DEPOT,
                duration=DIST_DATA,
                demand=demand_dict,
                ist=vehicles_start_times,
                permutations=best,
                demand_dict=demand_dict,
                customer_list=customer_list,
                k_lower_limit=k_lower_limit,
                max_k=max_k,
                population_count=population_count,
            )
            for i in inputs
        )

        current_best_entries = []
        for elem in processed_list:

            # sort the results based on duration of sequences  (i.e. x[2])
            elem = sorted(elem, key=lambda x: x[2], reverse=False)

            current_best_entries.append(elem[0][2])
            best.append(copy.deepcopy(elem[0]))
            # save the best results of the second iteration phase in the new_best list
            new_best.append(copy.deepcopy(elem[0]))

        iteration_count = iteration_count + 1

        if all_equal(current_best_entries) and num_cores != 1:
            # the program runs in parallel GA TDVRP mode
            # all threads returned the same duration value as the best value
            if all_equal_count >= (ITERATION_COUNT // 4) // 4:
                # if the thread equality happened (ITERATION_COUNT//4)//4 many times
                # stop the second iteration phase
                # because the program converges to the same point over and over
                # no need to lose any time
                # compare first iteration results and second iteration results and return the better one
                break
            else:
                # thread equality count increased
                all_equal_count = all_equal_count + 1

    print("------------------------------ SECOND ITERATION PHASE IS COMPLETED ------------------------------")

    # sort the best results of the second iteration phase
    best_result_list_2 = sorted(new_best, key=lambda x: x[2], reverse=False)

    best_route_max_time = best_result_list_2[0][2]
    best_route_sum_time = best_result_list_2[0][3]
    best_vehicle_routes = best_result_list_2[0][4]
    best_vehicle_times = best_result_list_2[0][5]

    if best_route_max_time_r1 > best_route_max_time:
        print("SECOND ITERATION PHASE GENERATED A BETTER RESULT")
        print("FIRST ITERATION BEST: ", best_route_max_time_r1)
        print("SECOND ITERATION BEST: ", best_route_max_time)
    else:
        print("SECOND ITERATION PHASE DID NOT GENERATE A BETTER RESULT")
        print("FIRST ITERATION BEST: ", best_route_max_time_r1)
        print("SECOND ITERATION BEST: ", best_route_max_time)

        # get the results of the first iteration phase as the final result
        best_route_max_time = best_route_max_time_r1
        best_route_sum_time = best_route_sum_time_r1
        best_vehicle_routes = best_vehicle_routes_r1
        best_vehicle_times = best_vehicle_times_r1

    if best_vehicle_times is None:
        print("FINAL SOLUTION: No feasible solution")
    else:
        print(f"FINAL SOLUTION: Best route max time: {best_route_max_time}")
        print(f"FINAL SOLUTION: Best route sum time: {best_route_sum_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"FINAL SOLUTION: Route of vehicle {vehicle_id}: {vehicle_cycles}")
        for vehicle_id, vehicle_time in best_vehicle_times.items():
            print(f"FINAL SOLUTION: Time of vehicle {vehicle_id}: {vehicle_time}")

    end_time = datetime.now()
    exec_time = end_time - start_time
    print(f"Genetic Algorithm TDVRP Time: {exec_time}")

    print("------------------------------ GA TDVRP IS COMPLETED ------------------------------")
    return (best_route_max_time, best_route_sum_time, best_vehicle_routes, best_vehicle_times, str(exec_time))


if __name__ == "__main__":
    run()
