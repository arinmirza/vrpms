from typing import List, Tuple
from queue import PriorityQueue
from collections import defaultdict


class VehiclesPQ:
    def __init__(self, vehicles_start_times: List[float]) -> None:
        """
        Constructor of PQ for vehicles
        # How to use PQ: https://www.linode.com/docs/guides/python-priority-queue/

        :param vehicles_start_times: List of (expected) start times of the vehicle. If not specified, they are all
            assumed as zero.
        """
        self.m = len(vehicles_start_times)
        self.vehicles_start_times = vehicles_start_times
        self.vehicles = PriorityQueue()
        self.init_vehicles()

    def init_vehicles(self) -> None:
        """
        Initializes times of vehicles based on the given start times
        """
        while not self.vehicles.empty():
            self.vehicles.get()
        for i in range(self.m):
            self.vehicles.put((self.vehicles_start_times[i], i))

    def get_vehicle(self) -> Tuple[float, int]:
        """
        Gets the vehicle with the earliest available time

        :return: Vehicle available time and vehicle id
        """
        vehicle_t, vehicle_id = self.vehicles.get()
        return vehicle_t, vehicle_id

    def put_vehicle(self, vehicle_t: float, vehicle_id: int) -> None:
        """
        Pushes the vehicle back to the PQ along with available time

        :param vehicle_t: Vehicle available time
        :param vehicle_id: Vehicle id
        """
        self.vehicles.put((vehicle_t, vehicle_id))

    def get_route_and_vehicle_times(self) -> Tuple[float, float, defaultdict]:
        """
        Gets the vehicle with the earliest available time

        :return: Total time it takes to visit the locations for the latest driver, sum of the durations of each driver,
            the travel duration for each driver
        """
        vehicle_times = defaultdict(float)
        route_max_time, route_sum_time = 0, 0
        while not self.vehicles.empty():
            vehicle_t, vehicle_id = self.vehicles.get()
            vehicle_times[vehicle_id] = vehicle_t
            route_max_time = max(route_max_time, vehicle_t)  # "route_max_time = vehicle_t" should be fine (min-heap)
            route_sum_time += vehicle_t
        return route_max_time, route_sum_time, vehicle_times
