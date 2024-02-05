from api.database import DatabaseVRP
from src.genetic_algorithm.genetic_algorithm import run_GA


if __name__ == "__main__":

    # CASE-1 Unit Demand Benchmark Settings

    params = {"auth": "", "locations_key": 4, "durations_key": 3}

    # Retrieve data from database
    database = DatabaseVRP(params["auth"])
    locations = database.get_locations_by_id(params["locations_key"], {})
    durations = database.get_durations_by_id(params["durations_key"], {})

    capacities = [5, 5, 5]
    startTimes = [0, 0, 0]
    ignoredCustomers = [
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57
    ]
    completedCustomers = []
    multiThreaded = True

    result = run_GA(
        locations=locations,
        durations=durations,
        initial_start_times=startTimes,
        capacities=capacities,
        ignored_customers=ignoredCustomers,
        completed_customers=completedCustomers,
        start_node=None,
        mode="TDVRP",
        multithreaded=multiThreaded,
        iteration_count=48,
        random_perm_count=125,
        customers=None,
        cancelled_customers=[],
        do_load_unload=False,
        max_k=-1,
        k_lower_limit=True,
    )
