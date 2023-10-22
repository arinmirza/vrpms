# IMPORTS
import copy
from data_gen import get_dist_data
from datetime import datetime
from iteration_utilities import random_permutation
import math
import random

# libraries for parallel processing
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

#######################################################################################################################
#######################################################################################################################
# PARAMETERS AND DATA GENERATION
K = 3
Q = 100
VEHICLE_CAPACITY = 100
IGNORE_LONG_TRIP = True # used in the duration calculation method
RANDOM_PERM_COUNT = 10000  # Genetic Algorithm initial sample size
DIST_DATA = get_dist_data() # generate the distance data matrix
MIN_ENTRY_COUNT = 25 # used for deciding on making or skipping the selection & replacement step
ITERATION_COUNT = 10 # limits the number of iterations for the genetic algorithm
INF = float("inf")
N_TIME_SLICES = 12
DEPOT = (0, -1, "Depot")

NODES = [
    (1, 40, "Olympia"),
    (2, 50, "Freisinger Landstraße 90"),
    (3, 30, "Infineon Campeon"),
    (4, 30, "Hauptbahnhof"),
    (5, 30, "Messestadt"),
    (6, 10, "IKEA Brunnthal"),
    (7, 10, "Nymphenburger Schloss"),
    (8, 5, "Sendlinger Tor"),
    (9, 25, "Garching Forschungszentrum"),
    (10, 35, "Klinikum Großhadern"),
    (11, 10, "V2 IKEA Brunnthal"),
    (12, 10, "V2 Nymphenburger Schloss"),
    (13, 5, "V2 Sendlinger Tor"),
    (14, 25, "V2 Garching Forschungszentrum"),
    (15, 35, "V2 Klinikum Großhadern"),
    (16, 40, "V3 Olympia"),
    (17, 50, "V3 Freisinger Landstraße 90"),
    (18, 30, "V3 Infineon Campeon"),
    (19, 30, "V3 Hauptbahnhof"),
    (20, 30, "V3 Messestadt"),
    (21, 10, "V3 IKEA Brunnthal"),
    (22, 10, "V3 Nymphenburger Schloss"),
    (23, 5, "V3 Sendlinger Tor"),
    (24, 25, "V3 Garching Forschungszentrum"),
    (25, 35, "V3 Klinikum Großhadern"),
    (26, 10, "V3  IKEA Brunnthal"),
    (27, 10, "V3  Nymphenburger Schloss"),
    (28, 5, "V3  Sendlinger Tor"),
    (29, 25, "V3  Garching Forschungszentrum"),
    (30, 35, "V3  Klinikum Großhadern")

]

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

        permutations[index].append([current_fitness_level, current_fitness_level + probability_list_non_inf_values[index]])
        current_fitness_level = current_fitness_level + probability_list_non_inf_values[index]

    # fills in the rest of the probability range values for the remaining permutations in the list
    count = 0
    for index in range(len(probability_list_non_inf_values), len(permutations)):
        permutations[index].append([current_fitness_level, current_fitness_level + probability_list_inf_values[count]])
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

        if (end - start).seconds >= 10:
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
                if elem[4][0] <= rand <= elem[4][1] and elem[1]:
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

def swap_mutation(permutations):
    """
                  Select two random indices and swap these indices
                  If the mutated permutation has a longer duration than the previous permutation, simply revert the swap
                  If the mutated permutation has a smaller duration than the previous permutation, keep the mutation

                  :param permutations: all available permutations
    """

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
                a,b = calculate_duration(single_perm[0])

                # if the new duration is shorter than the previous one keep it
                if a < single_perm[2]:
                    single_perm[2], single_perm[1] = a, b

                # if the new duration is longer than the previous one revert the changes
                else:
                    temp = single_perm[0][pos1]
                    single_perm[0][pos1] = single_perm[0][pos2]
                    single_perm[0][pos2] = temp
            count = count + 1
    return permutations

def scramble_mutation(permutations):
    """
                      Select two random indices
                      Shuffle everything that stays between these two randomly selected indices

                      :param permutations: all available permutations
    """

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
                upper_part = single_perm[0][bound[1] + 1:]
                # get the portion to be reversed
                subpart = single_perm[0][bound[0]:bound[1] + 1]
                # scramble the related portion
                random.shuffle(subpart)

                # construct the permutation with the reversed portion
                single_perm[0] = lower_part + subpart + upper_part

                # calculate new duration and save
                a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b

            count = count + 1
    return permutations

def inversion_mutation(permutations):
    """
                          Select two random indices
                          Reverse everything that stays between these two randomly selected indices

                          :param permutations: all available permutations
    """

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
                a, b = calculate_duration(single_perm[0])
                single_perm[2], single_perm[1] = a, b

            count = count + 1

    return permutations

def genetic_algorithm(population):
    """
                          Apply Mutation and Selection & Replacement operations
                          based on the random probabilities generated

                          :param population: all available permutations
    """

    new_population = None # empty variable for the output population

    # assigned probabilities for each mutation option
    SWAP_MUTATION_PROB = (0, 0.33)
    INVERSION_MUTATION_PROB = (0.33, 0.66)
    SCRAMBLE_MUTATION_PROB = (0.66, 1)

    # assigned probabilities for each selection & replacement option
    SELECTION_PROB = (0, 0.25)
    REPLACEMENT_PROB = (0.25, 0.5)
    RANDOM_SELECTION_PROB = (0.5, 0.75)
    NO_SELECTION_REPLACEMENT_PROB = (0.5, 1)

    # generate random probabilities
    rand_phase_1 = random.uniform(0,1)
    rand_phase_2 = random.uniform(0,1)

    # PHASE 1 MUTATION
    updated_population = population
    if SWAP_MUTATION_PROB[0] <= rand_phase_1 <= SWAP_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying swap mutation...")
        updated_population = swap_mutation(population)
    elif INVERSION_MUTATION_PROB[0] <= rand_phase_1 <= INVERSION_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying inversion mutation...")
        updated_population = inversion_mutation(population)
    elif SCRAMBLE_MUTATION_PROB[0] <= rand_phase_1 <= SCRAMBLE_MUTATION_PROB[1]:
        #print("REPRODUCTION: applying scramble mutation...")
        updated_population = scramble_mutation(population)

    # PHASE 2 SELECTION & REPLACEMENT
    if len(updated_population) > MIN_ENTRY_COUNT:
        # if the number of permutations available is less than MIN_ENTRY_COUNT do not apply selection & replacement
        if SELECTION_PROB[0] <= rand_phase_2 <= SELECTION_PROB[1]:
            #print("SELECTION & REPLACEMENT: applying selection...")
            # first calculate the fitness value of all permutations
            population_with_fitness = calculate_fitness_level(updated_population)
            # then select permutations based on fitness value
            new_population = select_based_on_fitness_proportional(population_with_fitness)

            # post process the permutations
            for elem in new_population:
                if len(elem) > 4:
                    del elem[4]

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

def calculate_duration(perm, dist_data=DIST_DATA):
    """
        Calculates total time it takes to visit the locations in order and the route

        :param perm: The locations to visit in order
        :param dist_data: The locations to visit in order
    """

    perm = list(perm)
    last_node = 0
    route = [last_node]
    curr_time, curr_capacity = 0, Q

    for elem in perm:
        node = elem[0]
        req_capacity = 0 if node == 0 else 1
        if node == 0 and last_node == 0:
            continue
        curr_time_slip = int(curr_time / 60)
        if not IGNORE_LONG_TRIP:
            curr_time_slip = min(curr_time_slip, N_TIME_SLICES-1)
        if curr_time_slip >= N_TIME_SLICES or curr_capacity < req_capacity:
            return INF, None
        curr_time += dist_data[last_node][node][curr_time_slip]
        if node == 0:
            curr_capacity = Q
        else:
            curr_capacity -= req_capacity
        last_node = node
        route.append(node)

    return curr_time, route

def clean_permutations(permutations):
    """
            Removes all values from the previous iteration of the genetic algorithm

            :param permutations: all available permutations
    """

    # simply removes the additional data appended in the earlier iterations of the genetic algorithm
    for perm in permutations:
        if len(perm) == 5:
            del perm[4]

    return permutations

def run(permutations = None):
    """
                Main method that controls the mode of the genetic algorithm
                If no input is given than it starts with population generation and runs genetic algorithm
                If 'permutations' list is given then skips population generation and runs genetic algorithm

                :param permutations: all available permutations
    """

    # main method of the program
    # all threads run this method in parallel

    # if the given input to this method is none, then a new population is generated from scratch
    if permutations is None:
        NODES_LIST = []

        # there can be different number of tours in each permutation
        # the upper limit is K
        # any permutation between 1 tour and up to K tours are generated
        # the mutation operations work against infeasible solutions
        for k in range(0,K):
            current_NODES = copy.deepcopy(NODES)
            for _ in range(k):
                current_NODES.append(DEPOT)
            NODES_LIST.append(current_NODES)

        random_generated_perm = []

        print("Generating random population with size: ", RANDOM_PERM_COUNT)

        while len(random_generated_perm) <= RANDOM_PERM_COUNT:
            for elem in NODES_LIST:

                # random permutation is generated
                random_perm = random_permutation(elem)
                # converted to list
                random_perm = list(random_perm)
                # DEPOT is added to the beginning and to the end
                random_perm.insert(0, DEPOT)
                random_perm.append(DEPOT)

                # duration and shop indices are calculated
                total_dist, route = calculate_duration(perm=random_perm, dist_data=DIST_DATA)
                # constructed a tuple of three elements 1) permutation 2) shop indices 3) total duration
                random_perm_tuple = [random_perm, route, total_dist]
                random_generated_perm.append(random_perm_tuple)

        # generated permutation list is sorted based on total duration (i.e. x[2])
        random_generated_perm = sorted(random_generated_perm, key=lambda x: x[2], reverse=False)
        # generated tours of each permutation is calculated and saved
        get_tours(random_generated_perm)
        # genetic algorithm code is called
        res = genetic_algorithm(random_generated_perm)
        # temporary variables used in the last iteration of the genetic algorithm
        res = clean_permutations(res)
        # results are sorted based on total duration (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    else:
        # permutations exist, do not generate new data and continue with the given input
        res = genetic_algorithm(permutations)
        # temporary variables used in the last iteration of the genetic algorithm
        res = clean_permutations(res)
        # results are sorted based on total duration (i.e. x[2])
        res = sorted(res, key=lambda x: x[2], reverse=False)

    return res


if __name__ == '__main__':

    start_time = datetime.now() # used for runtime calculation
    entries = []

    # get the number of available cores
    num_cores = int(multiprocessing.cpu_count())

    # run num_cores many threads in parallel
    # at the beginning there exists no input for the run method, thus tqdm library does not prepare any inputs
    inputs = tqdm(num_cores*[1])
    processed_list = Parallel(n_jobs=num_cores)(delayed(run)() for i in inputs)

    # save the output of the current iteration
    entries.append(copy.deepcopy(processed_list))

    iteration_count = 0
    while iteration_count < ITERATION_COUNT:
        # tqdm library prepares the previously generated permutations for the next iteration
        inputs = tqdm(processed_list)
        processed_list = Parallel(n_jobs=num_cores)(delayed(run)(permutations) for permutations in inputs)

        #
        current_best_entries = []
        thread_index = 1
        for elem in processed_list:

            # calculate total element count and total sum
            total_elem_count = sum(1 if i[2] != math.inf else 0 for i in elem)
            total_sum = sum(i[2] if i[2] != math.inf else 0 for i in elem)


            if total_elem_count == 0:
                # prevents division by zero error in some cases
                total_elem_count = 1

            print("Thread: " + str(thread_index) + " and Current Average: " + str(total_sum/total_elem_count))
            print("-----------------------------------------")
            total_sum = 0
            # save the best entry of this current thread for the current iteration
            current_best_entries.append(elem[0])
            thread_index = thread_index + 1
        # save the last results of each thread
        entries.append(copy.deepcopy(processed_list))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        print("Number of Iterations Done: ", (iteration_count + 1))
        print("**********************************************")
        print("**********************************************")
        print("**********************************************")
        iteration_count = iteration_count + 1

    # All iterations are done
    # select the best results from the saved results of the iterations
    best_result_list = []
    for elem in entries:
        for pl in elem:
            sorted(pl, key=lambda x: x[2], reverse=False)
            for entry in pl:
                best_result_list.append([entry[2], entry[1]])

    # sort the best results and get the first element as the solution
    best_result_list = sorted(best_result_list, key=lambda x: x[0], reverse=False)

    print("BEST RESULT BELOW:")
    print(best_result_list[0])

    end_time = datetime.now()
    print(f"Time: {end_time - start_time}")
    print("1")