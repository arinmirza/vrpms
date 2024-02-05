from api.database import DatabaseVRP
from src.utilities.helper.result_2_output import vrp_result_2_output
from src.utilities.helper.locations_helper import convert_locations, get_demands_from_locations


def run(capacities, vehicles_start_times, all_tours):
    errors = []
    database = DatabaseVRP()
    duration = database.get_durations_by_id(id=3, errors=errors)
    locations = database.get_locations_by_id(id=4, errors=errors)
    new_locations = convert_locations(locations)
    load = get_demands_from_locations(duration, new_locations)
    vehicle_2_tours = {}
    for i in range(len(capacities)):
        vehicle_2_tours[i] = all_tours[i]
    vrp_result_dict = {"vehicles_routes": vehicle_2_tours}
    result = vrp_result_2_output(
        vehicles_start_times=vehicles_start_times,
        duration=duration,
        load=load,
        locations=new_locations,
        vrp_result=vrp_result_dict,
        capacities=capacities,
    )
    print(result)


if __name__ == "__main__":
    capacities = [5]
    vehicles_start_times = [0]
    all_tours = [
        [[0, 23, 24, 25, 38, 31, 0], [0, 30, 29, 42, 41, 39, 0], [0, 34, 50, 33, 32, 28, 0], [0, 46, 45, 47, 49, 35, 0],
         [0, 37, 21, 22, 26, 27, 0], [0, 36, 43, 44, 48, 40, 0]]
    ]
    run(capacities, vehicles_start_times, all_tours)
