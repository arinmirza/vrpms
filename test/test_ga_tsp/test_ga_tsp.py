from api.database import DatabaseVRP
from src.genetic_algorithm.genetic_algorithm import run_GA


if __name__ == "__main__":

    params = {
        "auth": "",
        "locations_key": 4,
        "durations_key": 3
    }

    # Retrieve data from database
    database = DatabaseVRP(params["auth"])
    locations = database.get_locations_by_id(params["locations_key"], {})
    durations = database.get_durations_by_id(params["durations_key"], {})

    capacities = [20]
    startTime_TSP = 0
    ignoredCustomers = []
    completedCustomers = []
    multiThreaded = False

    result = run_GA(locations=locations,
                    durations=durations,
                    initial_start_times=startTime_TSP,
                    capacities=capacities,
                    ignored_customers=ignoredCustomers,
                    completed_customers=completedCustomers,
                    start_node=4,
                    mode="TSP",
                    multithreaded=multiThreaded,
                    iteration_count=30,
                    random_perm_count=125,
                    customers=[1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                    cancelled_customers=[],
                    do_load_unload=True,
                    max_k=-1,  # len(capacities)*2,
                    k_lower_limit=True)