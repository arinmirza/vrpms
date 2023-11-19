from typing import List, Tuple
import random

DEPOT = 0
TIME_UNITS = 3600  # hour = 60*60 seconds
INF = float("inf")


def calculate_tour_duration(tour: List[int], duration: List[List[List[float]]], start_time: float) -> float:
    t = start_time
    last_node = tour[0]
    for node in tour[1:]:
        h = int(t / TIME_UNITS)
        t += duration[last_node][node][h]
        last_node = node
    return t


def update_tour_with_2opt(
    tour: List[int], i: int, j: int, duration: List[List[List[float]]], start_time: float
) -> Tuple[float, List[int]]:
    tour_new = tour[: i + 1] + tour[j:i:-1] + tour[j + 1 :]
    t_new = calculate_tour_duration(tour=tour_new, duration=duration, start_time=start_time)
    return t_new, tour_new


def update_tour_with_exchange(
    tour: List[int], i: int, j: int, duration: List[List[List[float]]], start_time: float
) -> Tuple[float, List[int]]:
    tour_new = tour.copy()
    tour_new[i], tour_new[j] = tour[j], tour[i]
    t_new = calculate_tour_duration(tour=tour_new, duration=duration, start_time=start_time)
    return t_new, tour_new


def compute_nearest_neighbor_tour(
    customers: List[int], start_node: int, duration: List[List[List[float]]], start_time: float
) -> Tuple[float, List[int]]:
    t = start_time
    tour = [start_node]
    last_node = start_node
    for _ in range(len(customers)):
        best_city = None
        min_duration = INF
        h = int(t / TIME_UNITS)
        for node in customers:
            if node not in tour and duration[last_node][node][h] < min_duration:
                best_city = node
                min_duration = duration[last_node][node][h]
        t += min_duration
        tour.append(best_city)
        last_node = best_city
    h = int(t / TIME_UNITS)
    t += duration[last_node][DEPOT][h]
    tour.append(DEPOT)
    return t, tour


def compute_successive_insertion_tour(
    customers: List[int], start_node: int, duration: List[List[List[float]]], start_time: float
) -> Tuple[float, List[int]]:
    tour = [start_node, DEPOT]
    for node in customers:
        best_index = None
        min_duration = INF
        for i in range(1, len(tour)):
            tour_new = tour[:i] + [node] + tour[i:]
            t_new = calculate_tour_duration(tour=tour_new, duration=duration, start_time=start_time)
            if t_new < min_duration:
                best_index = i
                min_duration = t_new
        tour = tour[:best_index] + [node] + tour[best_index:]
    t = calculate_tour_duration(tour=tour, duration=duration, start_time=start_time)
    return t, tour


def compute_random_tour(
    customers: List[int], start_node: int, duration: List[List[List[float]]], start_time: float
) -> Tuple[float, List[int]]:
    tour = customers.copy()
    random.shuffle(tour)
    tour.insert(0, start_node)
    tour.append(DEPOT)
    t = calculate_tour_duration(tour=tour, duration=duration, start_time=start_time)
    return t, tour
