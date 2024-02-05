from api.database import DatabaseVRP
from src.genetic_algorithm.genetic_algorithm import run_GA


if __name__ == "__main__":

    # CASE-1 TSP Benchmark Settings

    params = {"auth": "", "locations_key": 4, "durations_key": 3}

    # Retrieve data from database
    database = DatabaseVRP(params["auth"])
    locations = database.get_locations_by_id(params["locations_key"], {})
    durations = database.get_durations_by_id(params["durations_key"], {})

    capacities = [0]
    startTime_TSP = 0
    ignoredCustomers = []
    completedCustomers = []
    multiThreaded = False

    result = run_GA(
        locations=locations,
        durations=durations,
        initial_start_times=startTime_TSP,
        capacities=capacities,
        ignored_customers=ignoredCustomers,
        completed_customers=completedCustomers,
        start_node=None,
        mode="TSP",
        multithreaded=multiThreaded,
        iteration_count=30,
        random_perm_count=125,
        customers=[1, 2, 3, 4, 5],
        cancelled_customers=[],
        do_load_unload=True,
        max_k=-1,
        k_lower_limit=True,
    )
