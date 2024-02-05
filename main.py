from api.database import DatabaseVRP
from src.utilities.helper.result_2_output import vrp_result_2_output
from src.utilities.helper.locations_helper import convert_locations, get_demands_from_locations


def run(capacities, vehicles_start_times, all_tours, durations_query_row_id, locations_query_row_id):
    errors = []
    database = DatabaseVRP()
    duration = database.get_durations_by_id(id=durations_query_row_id, errors=errors)
    locations = database.get_locations_by_id(id=locations_query_row_id, errors=errors)
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
        [
            [0, 50, 33, 32, 31, 38, 0],
            [0, 28, 49, 46, 45, 47, 0],
            [0, 34, 36, 39, 35, 40, 0],
            [0, 23, 24, 25, 27, 26, 0],
            [0, 30, 29, 21, 37, 22, 0],
            [0, 42, 41, 48, 43, 44, 0],
        ]
    ]
    durations_query_row_id = 3
    locations_query_row_id = 4
    run(capacities, vehicles_start_times, all_tours, durations_query_row_id, locations_query_row_id)
