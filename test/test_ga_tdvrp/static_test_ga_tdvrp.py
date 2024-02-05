from api.database import DatabaseVRP
from src.genetic_algorithm.genetic_algorithm import run_GA


if __name__ == "__main__":

    # Static Dynamic Duration Data Comparison Case

    params = {"auth": "", "locations_key": 4, "durations_key": 4}

    # Retrieve data from database
    database = DatabaseVRP(params["auth"])
    locations = database.get_locations_by_id(params["locations_key"], {})
    durations = database.get_durations_by_id(params["durations_key"], {})

    capacities = [5]
    startTimes = [0]
    ignoredCustomers = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,

        51,
        52,
        53,
        54,
        55,
        56,
        57,
    ]
    completedCustomers = []
    multiThreaded = False

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
        iteration_count=144,
        random_perm_count=125,
        customers=None,
        cancelled_customers=[],
        do_load_unload=False,
        max_k=-1,
        k_lower_limit=True,
    )
