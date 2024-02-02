# Genetic Algorithm TSP
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

# Imports: Libraries for Parallel Processing
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm


# Basic Variable Definitions
MIN_ENTRY_COUNT = 25 # used for deciding on making or skipping the selection & replacement step
INF = float("inf")
N_TIME_SLICES = 12
N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60 minutes
DEPOT = 0

#######################################################################################################################
#######################################################################################################################
# GENETIC ALGORITHM LOGIC

def random_selection(permutations, sel_count, already_selected = []):
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

        if not len(permutations[index])>=7:

            permutations[index].append([current_fitness_level, current_fitness_level + probability_list_non_inf_values[index]])
            current_fitness_level = current_fitness_level + probability_list_non_inf_values[index]

        else:
            permutations[index][6] = ([current_fitness_level, current_fitness_level + probability_list_non_inf_values[index]])
            current_fitness_level = current_fitness_level + probability_list_non_inf_values[index]

    # fills in the rest of the probability range values for the remaining permutations in the list
    count = 0
    for index in range(len(probability_list_non_inf_values), len(permutations)):

        if not len(permutations[index])>=7:
            permutations[index].append([current_fitness_level, current_fitness_level + probability_list_inf_values[count]])
            current_fitness_level = current_fitness_level + probability_list_inf_values[count]

        else:
            permutations[index][6] = ([current_fitness_level, current_fitness_level + probability_list_inf_values[count]])
            current_fitness_level = current_fitness_level + probability_list_inf_values[count]

        count = count + 1

    return permutations

def calculate_fitness_level(remaining_permutations):
    """
             Based on the previously calculated duration information, calculate the fitness level of each permutation

            :param remaining_permutations: all available permutations
    """

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

            if inf_starts_at_index == 0: # if it has been already changed then do not change it again
                inf_starts_at_index = index

        # store the non-reversed fitness level
        probability_list.append(fitness_level)

    # find the original/adjusted/reversed fitness levels
    remaining_permutations = reverse_insert_probability_list(remaining_permutations, probability_list, inf_starts_at_index)

    return remaining_permutations

def select_based_on_fitness_proportional(permutations):
    """
                 Select a predefined number of permutations from the given permutations list

                :param permutations: all available permutations
    """

    start = datetime.now()
    mode = "FITNESS"
    selection_len = int(len(permutations)*5 / 8)
    selected = []

    # continue fitness proportional selection until the selection length is reached
    while len(selected) < selection_len:

        end = datetime.now()

        if (end - start).seconds >= 0.6:
            # current implementation of the fitness proportional method might take some time
            # current time limit is 10 seconds
            # if the threshold is exceeded than selection mode is switched to RANDOM selection
            mode = "RANDOM"
            break

        else: # time limit has not reached, continue fitness proportional selection
            # generate random number between 0 and 1
            rand = random.uniform(0, 1)

            # find the permutation which has this value in its own fitness range
            for index in range(0, len(permutations)):
                elem = permutations[index]
                if elem[6][0] <= rand <= elem[6][1] and elem[1]:
                    selected.append(elem)
                    break

    if mode == "RANDOM":
        return random_selection(permutations = permutations, sel_count=selection_len, already_selected=selected)

    return selected

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

def swap_mutation(permutations, VST, dist_data, M, Q, load, demand_dict, sn, cancelled_customers, do_load_unload):
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
        while count < 10:  # threshold for the number of inversion mutation to be applied, for now it is 10
            # select two random positions
            # indices 0 and -1 are not included
            pos1 = random.randint(1, len(single_perm[0])-1)
            pos2 = random.randint(1, len(single_perm[0])-1)

            # if two positions are not equal and none of the positions equal to DEPOT
            if pos1 != pos2 and single_perm[0][pos1] != DEPOT and single_perm[0][pos2] != DEPOT:

                # swap the indices
                temp = single_perm[0][pos1]
                single_perm[0][pos1] = single_perm[0][pos2]
                single_perm[0][pos2] = temp
                # calculate the new duration
                a,b, route_sum_time, vehicle_routes, vehicle_times  = calculate_duration(permutation = single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q, load=load, demand_dict=demand_dict, sn=sn, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)

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

def scramble_mutation(permutations, VST, dist_data, M, Q, load, demand_dict, sn, cancelled_customers, do_load_unload):
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
        while count < 1: # threshold for the number of inversion mutation to be applied, for now it is 1
            # select two random positions
            # indices 0 and -1 are not included

            pos1 = random.randint(1, len(single_perm[0])-1)
            pos2 = random.randint(1, len(single_perm[0])-1)

            # save the lower and upper bounds as a pair
            bound = (pos1, pos2) if pos1 < pos2 else (pos2, pos1)

            if pos1 != pos2:
                # get the part before the selected portion
                lower_part = single_perm[0][0:bound[0]]
                # get the part after the selected portion
                upper_part = single_perm[0][bound[1] + 1:]
                # get the portion to be reversed
                subpart = single_perm[0][bound[0]:bound[1] + 1]
                # scramble the related portion
                random.shuffle(subpart)

                # construct the permutation with the reversed portion
                single_perm[0] = lower_part + subpart + upper_part

                # calculate new duration and save
                a, b, route_sum_time, vehicle_routes, vehicle_times= calculate_duration(single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=load, demand_dict=demand_dict, sn=sn, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times

            count = count + 1
    return permutations

def inversion_mutation(permutations,  VST, dist_data, M, Q,load, demand_dict, sn,  cancelled_customers, do_load_unload):
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
        #single_perm = [single_perm]
        count = 0
        while count < 1: # threshold for the number of inversion mutation to be applied, for now it is 1
            # select two random positions
            # indices 0 and -1 are not included

            pos1 = random.randint(1, len(single_perm[0])-1)
            pos2 = random.randint(1, len(single_perm[0])-1)

            # save the lower and upper bounds as a pair
            bound = (pos1, pos2) if pos1 < pos2 else (pos2, pos1)

            if pos1 != pos2:

                # get the part before the selected portion
                lower_part = single_perm[0][0:bound[0]]
                # get the part after the selected portion
                upper_part = single_perm[0][bound[1]+1:]
                # get the portion to be reversed
                subpart = single_perm[0][bound[0]:bound[1]+1]
                # reverse the related portion
                list.reverse(subpart)
                # construct the permutation with the reversed portion
                single_perm[0] = lower_part + subpart + upper_part

                # calculate new duration and save
                a, b, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=load, demand_dict=demand_dict, sn=sn, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times

            count = count + 1

    return permutations

def genetic_algorithm(population, N, M, k, q, W, duration, demand, ist, demand_dict, sn, cancelled_customers, do_load_unload):
    """
                          Apply Mutation and Selection & Replacement operations
                          based on the random probabilities generated

                          :param population: all available permutations
    """

    Q = q
    M = M
    DIST_DATA = duration
    LOAD = demand
    vehicles_start_times = ist

    new_population = None # empty variable for the output population

    # assigned probabilities for each mutation option
    SWAP_MUTATION_PROB = (0, 0.33)
    INVERSION_MUTATION_PROB = (0.33, 0.66)
    SCRAMBLE_MUTATION_PROB = (0.66, 1)

    # assigned probabilities for each selection & replacement option
    SELECTION_PROB = (0, 0)
    REPLACEMENT_PROB = (0, 0.5)
    RANDOM_SELECTION_PROB = (0.5, 0.75)
    NO_SELECTION_REPLACEMENT_PROB = (0.75, 1)

    # generate random probabilities
    rand_phase_1 = random.uniform(0,1)
    rand_phase_2 = random.uniform(0,1)

    # PHASE 1 MUTATION
    updated_population = population
    if SWAP_MUTATION_PROB[0] <= rand_phase_1 <= SWAP_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying swap mutation...")
        updated_population = swap_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD, demand_dict=demand_dict, sn=sn,  cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)
    elif INVERSION_MUTATION_PROB[0] <= rand_phase_1 <= INVERSION_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying inversion mutation...")
        updated_population = inversion_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD, demand_dict=demand_dict, sn=sn, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)
    elif SCRAMBLE_MUTATION_PROB[0] <= rand_phase_1 <= SCRAMBLE_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying scramble mutation...")
        updated_population = scramble_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD, demand_dict=demand_dict, sn=sn, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)

    # PHASE 2 SELECTION & REPLACEMENT
    if len(updated_population) > MIN_ENTRY_COUNT:
        # if the number of permutations available is less than MIN_ENTRY_COUNT do not apply selection & replacement
        if SELECTION_PROB[0] <= rand_phase_2 <= SELECTION_PROB[1]:
            #print("SELECTION & REPLACEMENT: applying selection...")
            # first calculate the fitness value of all permutations
            population_with_fitness = calculate_fitness_level(updated_population)
            # then select permutations based on fitness value
            new_population = select_based_on_fitness_proportional(population_with_fitness)
            pass

        elif REPLACEMENT_PROB[0] <= rand_phase_2 <= REPLACEMENT_PROB[1]:
            #print("SELECTION & REPLACEMENT: applying replacement...")
            new_population = deterministic_best_n_replacement(updated_population)

        elif RANDOM_SELECTION_PROB[0] <= rand_phase_2 <= RANDOM_SELECTION_PROB[1]:
            #print("SELECTION & REPLACEMENT: applying random selection...")
            new_population = random_selection(updated_population, (len(updated_population)*5/8), already_selected=[])

        elif NO_SELECTION_REPLACEMENT_PROB[0] <= rand_phase_2 <= NO_SELECTION_REPLACEMENT_PROB[1]:
            #print("SELECTION & REPLACEMENT: no operation...")
            new_population = updated_population
    else:
        new_population = updated_population

    return new_population

#######################################################################################################################
#######################################################################################################################
# DURATION CALCULATION AND RUN

LOADING_TIME_INIT = 30
LOADING_TIME_PER_UNIT = 10
UNLOADING_DEPOT_TIME_INIT = 30
UNLOADING_DEPOT_TIME_PER_UNIT = 10
UNLOADING_CUSTOMER_TIME_INIT = 60
UNLOADING_CUSTOMER_TIME_PER_UNIT = 10

def calculate_duration_load_unload_tsp(
    current_time: float, #vehicle start time
    current_location: int, #start node
    perm: List[int],
    duration: List[List[List[float]]],
    load: List[int],
    ignore_long_trip: bool,
    do_loading_unloading: bool,
    cancelled_customers: List[int],
    demand_dict: Dict[int, int]
) -> Tuple[float, float, Optional[defaultdict], Optional[defaultdict]]:
    """
    Calculates total time it takes to visit the locations and the route for the given order of customers

    :param current_time: Current time
    :param current_location: Current (starting) location
    :param perm: Customers to be visited in order
    :param duration: Dynamic duration data of NxNx12
    :param load: Loads of locations
    :param ignore_long_trip: Flag to ignore long trips
    :param do_loading_unloading: Spend time to do loading/unloading at the current_location
    :param cancelled_customers: Customers where regarding orders are cancelled
    :return: Total time it takes to visit the locations in the given order and the corresponding route
    """
    current_time_start = copy.deepcopy(current_time)
    route = [current_location] + perm + [DEPOT]
    last_node = current_location

    if do_loading_unloading:
        if current_location != DEPOT:
            current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * demand_dict[current_location]
        else:
            total_load = 0
            for customer in route:
                total_load += demand_dict[customer]
            if total_load > 0:
                current_time += LOADING_TIME_INIT + LOADING_TIME_PER_UNIT * total_load

    for node in route[1:]:
        hour = int(current_time / TIME_UNITS)
        if not ignore_long_trip:
            hour = min(hour, N_TIME_ZONES - 1)
        if hour >= N_TIME_ZONES:
            return INF, None
        current_time += duration[last_node][node][hour]
        if node != DEPOT:
            current_time += UNLOADING_CUSTOMER_TIME_INIT + UNLOADING_CUSTOMER_TIME_PER_UNIT * demand_dict[node]
        else:
            total_load = 0
            for customer in cancelled_customers:
                total_load += demand_dict[customer]
            if total_load > 0:
                current_time += UNLOADING_DEPOT_TIME_INIT + UNLOADING_DEPOT_TIME_PER_UNIT * total_load
        last_node = node

    if ignore_long_trip and current_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, None

    tour_len = current_time-current_time_start
    tour_len_dict = {}
    tour_len_dict[0] = tour_len

    tour_dict = {}
    tour_dict[0] = route
    return current_time, perm, tour_dict, tour_len

def calculate_duration(permutation, VST, dist_data, M, Q, load, demand_dict,sn, cancelled_customers, do_load_unload):

    route=[]
    for elem in permutation:
        node = elem
        route.append(node)

    if VST is None:
        VST = [0 for _ in range(M)]
    else:
        assert len(VST) == M, f"Size of the vehicles_start_times should be {M}"

    if not type(VST) == float:
        vehicles_start_times = VST[0]

    route_max_time, route, vehicle_routes, vehicle_times = calculate_duration_load_unload_tsp(current_time=vehicles_start_times, current_location=sn, perm=permutation, duration=dist_data, load = load, ignore_long_trip=False, do_loading_unloading=do_load_unload, cancelled_customers=cancelled_customers, demand_dict=demand_dict)

    return route_max_time, permutation, route_max_time, vehicle_routes, vehicle_times

def check_neighbor(perm):
    """
            Randomly generated permutations can not have two DEPOT nodes side by side.
            In that case shift places.
            This method returns if two DEPOT objects are neighbor to each other.
    """

    for i in range(1, len(perm)):
        if perm[i] == perm[i-1] == DEPOT:
            return False

    if perm[0] == DEPOT or perm[-1] == DEPOT:
        return False

    return True

def ga(N, M, k, q, W, duration, ist, start_node, customer_list, population_count, demand_dict, cancelled_customers=[], do_load_unload=True, permutations = None):
    """
                Main method that controls the mode of the genetic algorithm
                If no input is given than it starts with population generation and runs genetic algorithm
                If 'permutations' list is given then skips population generation and runs genetic algorithm

                :param permutations: all available permutations
    """

    # main method of the program
    # all threads run this method in parallel

    N = N  # number of shops to be considered
    K = k # number of tours to be considered
    Q = q # capacity of vehicle = N
    M = M # number of vehicles = 1
    DEPOT = W # DEPOT index
    DIST_DATA = duration # duration data
    LOAD = demand_dict # demands
    vehicles_start_times = ist # start times
    RANDOM_PERM_COUNT = population_count

    # if the given input to this method is none, then a new population is generated from scratch
    if permutations is None:
        NODES = []
        if len(customer_list) != 0:
            # there exists a user set customer list, use it directly
            NODES = copy.deepcopy(customer_list)
        else:
            # user set customer list does not exits, use N
            NODES.extend(range(1, N + 1))


        NODES_LIST = []
        NODES_LIST.append(NODES)
        random_generated_perm = []

        while len(random_generated_perm) <= RANDOM_PERM_COUNT:

            for elem in NODES_LIST:

                random_perm = random_permutation(elem)
                random_perm = list(random_perm)

                # duration and shop indices are calculated
                total_dist, route, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(permutation=random_perm, dist_data=DIST_DATA, VST= vehicles_start_times, M=M ,Q=Q, load=LOAD, demand_dict=demand_dict, sn=start_node, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)

                # constructed the tour information list
                random_perm_tuple = [route, route, total_dist, route_sum_time, vehicle_routes, vehicle_times]

                random_generated_perm.append(random_perm_tuple)

        # sort the set based on duration of sequences (i.e. x[2])
        random_generated_perm = sorted(random_generated_perm, key=lambda x: x[2], reverse=False)

        # genetic algorithm code is called
        res = genetic_algorithm(population = random_generated_perm, N= N, M= M, k= K, q= Q, W= DEPOT, duration= DIST_DATA, demand= LOAD, ist= vehicles_start_times, demand_dict=demand_dict, sn = start_node, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)

        # results are sorted based on duration of sequences  (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    else:
        # permutations exist, do not generate new data and continue with the given input
        res = genetic_algorithm(population = permutations, N= N, M= M, k= K, q= Q, W= DEPOT, duration= DIST_DATA, demand= LOAD, ist= vehicles_start_times, demand_dict=demand_dict, sn=start_node, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload)
        # results are sorted based on duration of sequences  (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    return res

def run(N, M, k, q, W, duration, ist, multithreaded, demand_dict, start_node = None, customer_list = [], cancelled_customers = [], do_load_unload = True, population_count=125, iteration_count=15):
    N = N  # number of shops to be considered
    K = k # number of tours to be considered
    Q = q # capacity of the vehicle = N
    M = M # number of vehicles = 1
    DEPOT = W # DEPOT index
    DIST_DATA = duration # duration data
    vehicles_start_times = ist
    ITERATION_COUNT = iteration_count

    start_time = datetime.now()  # used for runtime calculation

    # set the number of cores to be used
    if multithreaded:
        # get the number of available cores
        num_cores = int(multiprocessing.cpu_count())
    else:
        num_cores = 1

    # run num_cores many threads in parallel
    # at the beginning there exists no input for the ga method, permutations will be equal to None
    inputs = tqdm(num_cores * [1], disable=True)
    processed_list = Parallel(n_jobs=num_cores)(delayed(ga)(N = N, M = M, k = K, q = Q, W = DEPOT, duration = DIST_DATA, ist = vehicles_start_times, start_node = start_node, customer_list = customer_list, permutations=None, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload, demand_dict=demand_dict, population_count=population_count) for i in inputs)

    iteration_count = 0
    best = []

    while iteration_count < ITERATION_COUNT:

        inputs = tqdm(processed_list, disable=True)
        processed_list = Parallel(n_jobs=num_cores)(delayed(ga)(N = N, M = M, k = K, q = Q, W = DEPOT, duration = DIST_DATA, ist = vehicles_start_times, start_node = start_node, customer_list = customer_list, permutations=i, cancelled_customers=cancelled_customers, do_load_unload=do_load_unload, demand_dict=demand_dict, population_count=population_count) for i in inputs)

        for elem in processed_list:

            elem = sorted(elem, key=lambda x: x[2], reverse=False)

            best.append(copy.deepcopy(elem[0]))

        iteration_count = iteration_count + 1

    # sort the best results
    best_result_list = sorted(best, key=lambda x: x[2], reverse=False)

    best_route_max_time = best_result_list[0][2]
    best_route_sum_time = best_result_list[0][3]
    best_vehicle_routes = best_result_list[0][4]
    best_vehicle_times = best_result_list[0][5]

    end_time = datetime.now()
    exec_time = end_time - start_time


    print("GA TSP: Best route", best_route_max_time)
    print("GA TSP: Best sum time",best_route_sum_time)
    print("GA TSP: Best routes",best_vehicle_routes)
    print("GA TSP: Best vehicle times",best_vehicle_times)
    print("GA TSP: exec time",exec_time)
    return (
        best_route_max_time,
        best_route_sum_time,
        best_vehicle_routes,
        best_vehicle_times,
        str(exec_time)
    )


if __name__ == '__main__':
    run(multithreaded=True)
