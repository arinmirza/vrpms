#Genetic Algorithm with Dynamic Input Size, Vehicle Priority Queueu and Updated Fake Data Generation

# IMPORTS
import copy
from datetime import datetime
from iteration_utilities import random_permutation
import math
import random
from typing import List, Literal, Optional, Tuple
from collections import defaultdict

# Libraries for Parallel Processing
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

# Project Files to be Imported
from src.utilities.vrp_helper import get_based_and_load_data
from data.NODES import get_nodes
from src.vrp.vehicles_pq import VehiclesPQ

# PARAMETERS AND DATA GENERATION


IGNORE_LONG_TRIP = True # used in the duration calculation method
RANDOM_PERM_COUNT = 125 # Genetic Algorithm initial sample size
PER_KM_TIME = 0.25
#DIST_DATA, LOAD = get_based_and_load_data(input_file_load = None, n=N+1, per_km_time=PER_KM_TIME) # generate the distance data matrix
MIN_ENTRY_COUNT = 25 # used for deciding on making or skipping the selection & replacement step
ITERATION_COUNT = 48  # limits the number of iterations for the genetic algorithm
INF = float("inf")
N_TIME_SLICES = 12
#DEPOT_TUPLE = (0, -1, "Depot")

N_TIME_ZONES = 12  # hours = time slices
TIME_UNITS = 3600  # hour = 60 minutes
DEPOT = 0

#NODES = get_nodes()
#NODES = NODES[:N]

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
    while len(already_selected) < sel_count:
        rand_index = random.randint(0, len(permutations)-1)
        already_selected.append(permutations[rand_index])

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
    #print("SELECTION: Calculating fitness level...")

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

    #find the original/adjusted/reversed fitness levels
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

def swap_mutation(permutations, VST, dist_data, M, Q, load):
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
            pos1 = random.randint(1, len(single_perm[0])-2)
            pos2 = random.randint(1, len(single_perm[0])-2)

            # if two positions are not equal and none of the positions equal to DEPOT
            if pos1 != pos2 and single_perm[0][pos1] != DEPOT and single_perm[0][pos2] != DEPOT:

                # swap the indices
                temp = single_perm[0][pos1]
                single_perm[0][pos1] = single_perm[0][pos2]
                single_perm[0][pos2] = temp
                # calculate the new duration
                a,b, route_sum_time, vehicle_routes, vehicle_times  = calculate_duration(permutation = single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q, load=load)
                #a, b = calculate_duration(single_perm[0])

                # if the new duration is shorter than the previous one keep it
                if a < single_perm[2]:
                    single_perm[2], single_perm[1] = a, b
                    single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times
                    #single_perm.append(route_sum_time)
                    #single_perm.append(vehicle_routes)
                    #single_perm.append(vehicle_times)

                # if the new duration is longer than the previous one revert the changes
                else:
                    temp = single_perm[0][pos1]
                    single_perm[0][pos1] = single_perm[0][pos2]
                    single_perm[0][pos2] = temp
            count = count + 1
    return permutations

def scramble_mutation(permutations, VST, dist_data, M, Q, load):
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
                    lower_part = single_perm[0][0:bound[0]]
                    # get the part after the selected portion
                    upper_part = single_perm[0][bound[1] + 1:]
                    # get the portion to be reversed
                    subpart = single_perm[0][bound[0]:bound[1] + 1]
                    # scramble the related portion
                    random.shuffle(subpart)

                    old_perm = single_perm[0]
                    # construct the permutation with the reversed portion
                    new_perm = lower_part + subpart + upper_part

                    single_perm[0] = new_perm

                    if check_neighbor(single_perm[0], src = "scr"):
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
                a, b, route_sum_time, vehicle_routes, vehicle_times= calculate_duration(single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=load)
                #a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times
                #single_perm.append(route_sum_time)
                #single_perm.append(vehicle_routes)
                #single_perm.append(vehicle_times)

            count = count + 1
    return permutations

def inversion_mutation(permutations,  VST, dist_data, M, Q,load):
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
        while count < 1: # threshold for the number of inversion mutation to be applied, for now it is 1
            # select two random positions
            # indices 0 and -1 are not included
            pos1 = random.randint(1, len(single_perm[0]) - 2)
            pos2 = random.randint(1, len(single_perm[0]) - 2)

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
                a, b, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(single_perm[0], VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=load)
                #a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b
                single_perm[3], single_perm[4], single_perm[5] = route_sum_time, vehicle_routes, vehicle_times
                #single_perm.append(route_sum_time)
                #single_perm.append(vehicle_routes)
                #single_perm.append(vehicle_times)
            count = count + 1

    return permutations

def genetic_algorithm(population, N_in, M_in, k_in, q_in, W_in, duration_in, demand_in, ist_in):
    """
                          Apply Mutation and Selection & Replacement operations
                          based on the random probabilities generated

                          :param population: all available permutations
    """

    N = N_in  # number of shops to be considered
    K = k_in
    Q = q_in
    M = M_in
    DEPOT = W_in
    DIST_DATA = duration_in
    LOAD = demand_in
    vehicles_start_times = ist_in

    new_population = None # empty variable for the output population

    # assigned probabilities for each mutation option
    SWAP_MUTATION_PROB = (0, 0.33)
    INVERSION_MUTATION_PROB = (0.33, 0.66)
    SCRAMBLE_MUTATION_PROB = (0.66, 1)

    # assigned probabilities for each selection & replacement option
    SELECTION_PROB = (0, 0)
    REPLACEMENT_PROB = (0, 0.5)
    RANDOM_SELECTION_PROB = (0.5, 0.75)
    NO_SELECTION_REPLACEMENT_PROB = (0.5, 1)

    # generate random probabilities
    rand_phase_1 = random.uniform(0,1)
    rand_phase_2 = random.uniform(0,1)

    # PHASE 1 MUTATION
    updated_population = population
    if SWAP_MUTATION_PROB[0] <= rand_phase_1 <= SWAP_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying swap mutation...")
        updated_population = swap_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD)
    elif INVERSION_MUTATION_PROB[0] <= rand_phase_1 <= INVERSION_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying inversion mutation...")
        updated_population = inversion_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD)
    elif SCRAMBLE_MUTATION_PROB[0] <= rand_phase_1 <= SCRAMBLE_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying scramble mutation...")
        updated_population = scramble_mutation(population, VST = vehicles_start_times, dist_data = DIST_DATA, M=M, Q=Q,load=LOAD)

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
            # post process the permutations
            #for elem in new_population:
            #    if len(elem) > 4:
            #        del elem[4]

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
# HELPER FUNCTIONS
def get_tours(permutations):
    """
                              Find the tours of all permutations
                              Save this information in the given object

                              :param permutations: all available permutations
    """

    # returns the tour nodes and available capacity per tour
    state = "BEGINNING"

    all_tours = []

    for elem in permutations:
        current_tour = []
        for shop_index in range(0, len(elem[0])):

            if elem[0][shop_index] == DEPOT and state == "BEGINNING":
                state = "NEW_TOUR_STARTED"
                current_tour.append(elem[0][shop_index])

            elif elem[0][shop_index] == DEPOT and state == "NEW_TOUR_STARTED" and shop_index == len(elem[0]) - 1:
                # last element of the permutation is reached
                # the tour is stopped and saved
                state = "BEGINNING"
                current_tour.append(elem[0][shop_index])

                all_tours.append(current_tour)
                current_tour = []

            elif elem[0][shop_index] == DEPOT and state == "NEW_TOUR_STARTED" and shop_index != len(elem[0]) - 1:
                # last element of the permutation is NOT reached
                # the tour is stopped and saved
                # new tour has started
                state = "NEW_TOUR_STARTED"
                current_tour.append(elem[0][shop_index])

                all_tours.append(current_tour)
                current_tour = []
                current_tour.append(DEPOT)

            elif elem[0][shop_index] != DEPOT and state == "NEW_TOUR_STARTED":
                # last element of the permutation is NOT reached
                # the tour is NOT stopped
                # current shop is added and tour continues
                current_tour.append(elem[0][shop_index])
            else:
                pass

        elem.append(all_tours)
        all_tours = []

    return permutations


#######################################################################################################################
#######################################################################################################################
# DURATION CALCULATION AND RUN
def helper(
    q: int,
    m: int,
    ignore_long_trip: bool,
    cycles: List[List[int]],
    duration: List[List[List[float]]],
    load: List[int],
    vehicles_start_times: List[float],
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
    vehicle_times = defaultdict(float)

    # Initialize the PQ of vehicles (drivers) with given (expected) start time
    vehicles_pq = VehiclesPQ(vehicles_start_times)

    # Cycle: [DEPOT, customer_1, customer_2, ..., customer_k, DEPOT]
    # Cycles: [cycle_1, cycle_2, ...]
    for cycle in cycles:
        # Get the vehicle (driver) with the earliest available time
        vehicle_t, vehicle_id = vehicles_pq.get_vehicle()
        last_node = DEPOT
        curr_capacity = q
        # Go over each edge in the cycle
        for node in cycle[1:]:
            # Update capacity and check if it exceeds the initial capacity
            curr_capacity -= load[node]
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
            last_node = node
        # Update PQ with the chosen vehicle and updated time
        vehicles_pq.put_vehicle(vehicle_t, vehicle_id)
        vehicle_routes[vehicle_id].append(cycle)

    # Pull elements from PQ and update vehicle id to cycles and times mapping
    # route_max_time: max of duration among all vehicles (drivers)
    # route_sum_time: sum of duration of all vehicles (drivers)
    route_max_time, route_sum_time, vehicle_times = vehicles_pq.get_route_and_vehicle_times()

    # Check if it exceeds the number of time zones (based on ignore_long_trip)
    # Actually, it is not that necessary since all cycles checked
    if ignore_long_trip and route_max_time >= N_TIME_ZONES * TIME_UNITS:
        return INF, INF, None, None

    # Return :)
    return route_max_time, route_sum_time, vehicle_routes, vehicle_times


def calculate_duration_perm(
    perm: List[int],
    duration: List[List[List[float]]],
    vehicles_start_times: Optional[List[float]],
    q: int,
    m: int,
    load: List[int],
    ignore_long_trip: bool = False


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

    return helper(q, m, ignore_long_trip, cycles, duration, load, vehicles_start_times)

def calculate_duration(permutation, VST, dist_data, M, Q, load):

    #route = [0]
    route=[]
    for elem in permutation:
        node = elem
        route.append(node)

    if VST is None:
        VST = [0 for _ in range(M)]
    else:
        assert len(VST) == M, f"Size of the vehicles_start_times should be {M}"

    route_max_time, route_sum_time, vehicle_routes, vehicle_times = calculate_duration_perm(q=Q, m= M, perm=route, duration=dist_data, vehicles_start_times=VST, load = load)

    return route_max_time, route, route_sum_time, vehicle_routes, vehicle_times


def clean_permutations(permutations):
    """
            Removes all values from the previous iteration of the genetic algorithm

            :param permutations: all available permutations
    """

    # simply removes the additional data appended in the earlier iterations of the genetic algorithm
    #for perm in permutations:
    #    if len(perm) == 9:
    #        del perm[8]

    return permutations

def correct_neighbor_order(perm, index):

    # get the DEPOT element in the index position
    # shift to the right until hitting a non DEPOT node
    perm_old = perm
    for i in range(1, len(perm)-1):
        if perm[i] != DEPOT and perm[i+1] != DEPOT:
            del perm[index]
            perm.insert(i, DEPOT)

    return perm

def check_neighbor(perm, src = "def"):

    # randomly generated permutations can not have two DEPOT nodes side by side. In that case shift places.

    for i in range(1, len(perm)):
        if perm[i] == perm[i-1] == DEPOT:
            #perm = correct_neighbor_order(perm = perm, index = i)
            return False

    if src == "def":
        if perm[0] == DEPOT or perm[-1] == DEPOT:
            return False

    return True


def ga(N_in, M_in, k_in, q_in, W_in, duration_in, demand_in, ist_in, permutations = None):
    """
                Main method that controls the mode of the genetic algorithm
                If no input is given than it starts with population generation and runs genetic algorithm
                If 'permutations' list is given then skips population generation and runs genetic algorithm

                :param permutations: all available permutations
    """

    N = N_in  # number of shops to be considered
    K = k_in
    Q = q_in
    M = M_in
    DEPOT = W_in
    DIST_DATA = duration_in
    LOAD = demand_in
    vehicles_start_times = ist_in

    # main method of the program
    # all threads run this method in parallel

    # if the given input to this method is none, then a new population is generated from scratch
    if permutations is None:
        NODES_LIST = []

        # there can be different number of tours in each permutation
        # the upper limit is K
        # any permutation between 1 tour and up to K tours are generated
        # the mutation operations work against infeasible solutions

        NODES = []
        NODES.extend(range(1, N+1))

        #for k in range(0,K):
        #    current_NODES = copy.deepcopy(NODES)
        #    for _ in range(k):
        #        current_NODES.append(DEPOT)
        #    NODES_LIST.append(current_NODES)

        for _ in range(K-1):
            NODES.append(DEPOT)

        NODES_LIST.append(NODES)

        #NODES_LIST.append(NODES)
        random_generated_perm = []

        print("Generating random population with size: ", RANDOM_PERM_COUNT)

        while len(random_generated_perm) <= RANDOM_PERM_COUNT:
            for elem in NODES_LIST:

                # random permutation is generated
                random_perm = random_permutation(elem)
                random_perm = list(random_perm)

                while not check_neighbor(random_perm):
                    random_perm = random_permutation(elem)
                    random_perm = list(random_perm)

                # converted to list

                # DEPOT is added to the beginning and to the end
                random_perm.insert(0, DEPOT)
                random_perm.append(DEPOT)

                # duration and shop indices are calculated
                total_dist, route, route_sum_time, vehicle_routes, vehicle_times = calculate_duration(permutation=random_perm, dist_data=DIST_DATA, VST= vehicles_start_times, M=M ,Q=Q, load=LOAD)
                #total_dist, route = calculate_duration(permutation=random_perm, dist_data=DIST_DATA)
                # constructed a tuple of three elements 1) permutation 2) shop indices 3) total duration
                random_perm_tuple = [random_perm, route, total_dist, route_sum_time, vehicle_routes, vehicle_times]
                #random_perm_tuple = [random_perm, route, total_dist, route_sum_time, vehicle_routes, vehicle_times]
                random_generated_perm.append(random_perm_tuple)

        # generated permutation list is sorted based on total duration (i.e. x[2])
        random_generated_perm = sorted(random_generated_perm, key=lambda x: x[2], reverse=False)
        # generated tours of each permutation is calculated and saved
        get_tours(random_generated_perm)
        # genetic algorithm code is called
        res = genetic_algorithm(population = random_generated_perm, N_in = N, M_in = M, k_in = K, q_in = Q, W_in = DEPOT, duration_in = DIST_DATA, demand_in = LOAD, ist_in = vehicles_start_times)
        # temporary variables used in the last iteration of the genetic algorithm
        res = clean_permutations(res)
        # results are sorted based on total duration (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    else:
        # permutations exist, do not generate new data and continue with the given input
        res = genetic_algorithm(population = permutations, N_in = N, M_in = M, k_in = K, q_in = Q, W_in = DEPOT, duration_in = DIST_DATA, demand_in = LOAD, ist_in = vehicles_start_times)
        # temporary variables used in the last iteration of the genetic algorithm
        res = clean_permutations(res)
        # results are sorted based on total duration (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    return res



def run(N_in, M_in, k_in, q_in, W_in, duration_in, demand_in, ist_in):

    N = N_in  # number of shops to be considered
    K = k_in
    Q = q_in
    M = M_in
    DEPOT = W_in
    DIST_DATA = duration_in
    LOAD = demand_in
    vehicles_start_times = ist_in

    start_time = datetime.now()  # used for runtime calculation
    entries = []

    #if multithreaded:
        # get the number of available cores
    num_cores = int(multiprocessing.cpu_count())
    #else:
    #    num_cores = 1

    # run num_cores many threads in parallel
    # at the beginning there exists no input for the run method, thus tqdm library does not prepare any inputs
    inputs = tqdm(num_cores * [1])
    processed_list = Parallel(n_jobs=num_cores)(delayed(ga)(N_in = N, M_in = M, k_in = K, q_in = Q, W_in = DEPOT, duration_in = DIST_DATA, demand_in = LOAD, ist_in = vehicles_start_times, permutations=None) for i in inputs)

    # save the output of the current iteration
    #entries.append(copy.deepcopy(processed_list))

    iteration_count = 0

    best = []

    while iteration_count < ITERATION_COUNT:
        # tqdm library prepares the previously generated permutations for the next iteration
        inputs = tqdm(processed_list)
        processed_list = Parallel(n_jobs=num_cores)(delayed(ga)(N_in = N, M_in = M, k_in = K, q_in = Q, W_in = DEPOT, duration_in = DIST_DATA, demand_in = LOAD, ist_in = vehicles_start_times, permutations=i) for i in inputs)

        #
        current_best_entries = []
        thread_index = 1
        for elem in processed_list:

            # calculate total element count and total sum
            #total_elem_count = sum(1 if i[2] != math.inf else 0 for i in elem)
            #total_sum = sum(i[2] if i[2] != math.inf else 0 for i in elem)

            #if total_elem_count == 0:
                # prevents division by zero error in some cases
                #total_elem_count = 1
            elem = sorted(elem, key=lambda x: x[2], reverse=False)
            #print("Thread: " + str(thread_index) + " and Current Average: " + str(total_sum / total_elem_count))
            print("Thread: " + str(thread_index) + " and Current Best: " + str(elem[0][2]))
            best.append(copy.deepcopy(elem[0]))
            print("-----------------------------------------")
            total_sum = 0
            # save the best entry of this current thread for the current iteration
            #current_best_entries.append(elem[0])
            thread_index = thread_index + 1
        # save the last results of each thread
        #entries.append(copy.deepcopy(processed_list))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        print("Number of Iterations Done: ", (iteration_count + 1))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        iteration_count = iteration_count + 1

        if (iteration_count % 8) == 0 and iteration_count != ITERATION_COUNT:
            processed_list = Parallel(n_jobs=num_cores)(
                delayed(ga)(N_in=N, M_in=M, k_in=K, q_in=Q, W_in=DEPOT, duration_in=DIST_DATA, demand_in=LOAD,
                            ist_in=vehicles_start_times, permutations=None) for i in inputs)

        #if iteration_count == ITERATION_COUNT:
        #    processed_list = Parallel(n_jobs=num_cores)(
        #        delayed(ga)(N_in=N, M_in=M, k_in=K, q_in=Q, W_in=DEPOT, duration_in=DIST_DATA, demand_in=LOAD,
        #                    ist_in=vehicles_start_times, permutations=best) for i in inputs)
        #    ITERATION_COUNT = ITERATION_COUNT + 1

    best_result_list = sorted(best, key=lambda x: x[2], reverse=False)

    print("BEST RESULT BELOW:")
    # print(best_result_list[0])

    best_route_max_time = best_result_list[0][2]
    best_route_sum_time = best_result_list[0][3]
    best_vehicle_routes = best_result_list[0][4]
    best_vehicle_times = best_result_list[0][5]

    if best_vehicle_times is None:
        print("No feasible solution")
    else:
        print(f"Best route max time: {best_route_max_time}")
        print(f"Best route sum time: {best_route_sum_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"Route of vehicle {vehicle_id}: {vehicle_cycles}")
        for vehicle_id, vehicle_time in best_vehicle_times.items():
            print(f"Time of vehicle {vehicle_id}: {vehicle_time}")

    print("wowowowowowowoowowowow")

    best = sorted(best, key=lambda x: x[2], reverse=False)

    #best = best[0:int(len(best)/2)+1]

    #processed_list = [best[i:i + int(len(best)/num_cores)] for i in range(0, len(best), int(len(best)/num_cores))]

    iteration_count = 0

    from itertools import groupby

    def all_equal(iterable):
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

    all_equal_count = 0

    while iteration_count < ITERATION_COUNT/4:

        # tqdm library prepares the previously generated permutations for the next iteration
        inputs = tqdm(processed_list)
        #processed_list = Parallel(n_jobs=num_cores)(delayed(ga)(N_in = N, M_in = M, k_in = K, q_in = Q, W_in = DEPOT, duration_in = DIST_DATA, demand_in = LOAD, ist_in = vehicles_start_times, permutations=i) for i in inputs)

        processed_list = Parallel(n_jobs=num_cores)(
            delayed(ga)(N_in=N, M_in=M, k_in=K, q_in=Q, W_in=DEPOT, duration_in=DIST_DATA, demand_in=LOAD,
                        ist_in=vehicles_start_times, permutations=best) for i in inputs)

        #
        current_best_entries = []
        thread_index = 1
        for elem in processed_list:

            # calculate total element count and total sum
            #total_elem_count = sum(1 if i[2] != math.inf else 0 for i in elem)
            #total_sum = sum(i[2] if i[2] != math.inf else 0 for i in elem)

            #if total_elem_count == 0:
                # prevents division by zero error in some cases
                #total_elem_count = 1
            elem = sorted(elem, key=lambda x: x[2], reverse=False)
            #print("Thread: " + str(thread_index) + " and Current Average: " + str(total_sum / total_elem_count))
            print("Thread: " + str(thread_index) + " and Current Best: " + str(elem[0][2]))
            current_best_entries.append(elem[0][2])
            best.append(copy.deepcopy(elem[0]))
            print("-----------------------------------------")
            total_sum = 0
            # save the best entry of this current thread for the current iteration
            #current_best_entries.append(elem[0])
            thread_index = thread_index + 1

        #processed_list = [best[i:i + int(len(best) / num_cores)] for i in range(0, len(best), int(len(best) / num_cores))]

        #for elem in processed_list:
        #    elem = sorted(elem, key=lambda x: x[2], reverse=False)

        #processed_list = [plist[0: int(len(plist)/8)] for plist in processed_list]

        # save the last results of each thread
        #entries.append(copy.deepcopy(processed_list))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        print("Number of Iterations Done: ", (iteration_count + 1))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        iteration_count = iteration_count + 1

        if all_equal(current_best_entries):
            if all_equal_count >=5:
                break
            else:
                all_equal_count = all_equal_count +1


    # sort the best results and get the first element as the solution
    best_result_list = sorted(best, key=lambda x: x[2], reverse=False)

    #res = calculate_duration(permutation=)

    print("BEST RESULT BELOW:")
    #print(best_result_list[0])

    best_route_max_time = best_result_list[0][2]
    best_route_sum_time = best_result_list[0][3]
    best_vehicle_routes = best_result_list[0][4]
    best_vehicle_times = best_result_list[0][5]


    if best_vehicle_times is None:
        print("No feasible solution")
    else:
        print(f"Best route max time: {best_route_max_time}")
        print(f"Best route sum time: {best_route_sum_time}")
        for vehicle_id, vehicle_cycles in best_vehicle_routes.items():
            print(f"Route of vehicle {vehicle_id}: {vehicle_cycles}")
        for vehicle_id, vehicle_time in best_vehicle_times.items():
            print(f"Time of vehicle {vehicle_id}: {vehicle_time}")

    end_time = datetime.now()
    exec_time = end_time - start_time
    print(f"Time: {exec_time}")

    print("END")

    return (
        best_route_max_time,
        best_route_sum_time,
        best_vehicle_routes,
        best_vehicle_times,
        str(exec_time)
    )


if __name__ == '__main__':
    run()
