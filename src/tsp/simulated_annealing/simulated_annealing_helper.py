from typing import List, Tuple
import random

from src.utilities.helper.tsp_helper import route_solution_to_arrivals

DEPOT = 0
TIME_UNITS = 3600  # hour = 60*60 seconds
INF = float("inf")


def update_tour_with_2opt(tour: List[int], i: int, j: int) -> List[int]:
    tour_new = tour[: i + 1] + tour[j:i:-1] + tour[j + 1 :]
    return tour_new


def update_tour_with_exchange(tour: List[int], i: int, j: int) -> List[int]:
    tour_new = tour.copy()
    tour_new[i], tour_new[j] = tour[j], tour[i]
    return tour_new


def compute_nearest_neighbor_tour(
    customers: List[int],
    start_node: int,
    start_time: float,
    duration: List[List[List[float]]],
    load: List[int],
    do_loading_unloading: bool,
    cancelled_customers: List[int],
) -> List[int]:
    tour = [start_node]
    for _ in range(len(customers)):
        best_customer = None
        t_min = INF
        for customer in customers:
            if customer not in tour:
                tour_new = tour.copy() + [customer]
                _, t_new = route_solution_to_arrivals(
                    vehicle_start_time=start_time,
                    route=tour_new,
                    duration=duration,
                    load=load,
                    do_loading_unloading=do_loading_unloading,
                    cancelled_customers=cancelled_customers,
                )
                if t_new < t_min:
                    best_customer = customer
                    t_min = t_new
        tour.append(best_customer)
    tour.append(DEPOT)
    return tour


def compute_successive_insertion_tour(
    customers: List[int],
    start_node: int,
    start_time: float,
    duration: List[List[List[float]]],
    load: List[int],
    do_loading_unloading: bool,
    cancelled_customers: List[int],
) -> List[int]:
    tour = [start_node, DEPOT]
    for node in customers:
        best_index = None
        t_min = INF
        for i in range(1, len(tour)):
            tour_new = tour[:i] + [node] + tour[i:]
            _, t_new = route_solution_to_arrivals(
                vehicle_start_time=start_time,
                route=tour_new,
                duration=duration,
                load=load,
                do_loading_unloading=do_loading_unloading,
                cancelled_customers=cancelled_customers,
            )
            if t_new < t_min:
                best_index = i
                t_min = t_new
        tour = tour[:best_index] + [node] + tour[best_index:]
    return tour


def compute_random_tour(customers: List[int], start_node: int) -> List[int]:
    tour = customers.copy()
    random.shuffle(tour)
    tour = [start_node] + tour + [DEPOT]
    return tour
