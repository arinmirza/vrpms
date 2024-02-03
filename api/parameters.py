from api.helpers import get_parameter


def parse_common_vrp_parameters(content: dict, errors):
    return {
        "name": get_parameter("solutionName", content, errors),
        "auth": get_parameter("auth", content, errors, optional=True),
        "description": get_parameter("solutionDescription", content, errors),
        "locations": get_parameter("locations", content, errors, optional=True),
        "durations": get_parameter("durations", content, errors, optional=True),
        "locations_key": get_parameter("locationsKey", content, errors, optional=True),
        "durations_key": get_parameter("durationsKey", content, errors, optional=True),
        "capacities": get_parameter("capacities", content, errors),
        "start_times": get_parameter("startTimes", content, errors),
        "ignored_customers": get_parameter("ignoredCustomers", content, errors),
        "completed_customers": get_parameter("completedCustomers", content, errors),
    }


def parse_vrp_ga_parameters(content: dict, errors):
    return {
        "multi_threaded": get_parameter("multiThreaded", content, errors),
        "random_permutationCount": get_parameter("randomPermutationCount", content, errors),
        "iteration_count": get_parameter("iterationCount", content, errors),
        "max_k": get_parameter("max_k", content, errors),
        "k_lower_limit": get_parameter("k_lower_limit", content, errors),
    }


def parse_vrp_sa_parameters(content: dict, errors):
    return {}


def parse_vrp_aco_parameters(content: dict, errors):
    return {
        "n_hyperparams": get_parameter("n_hyperparams", content, errors),
        "aco_sols": get_parameter("aco_sols", content, errors, optional=True),
        "consider_depots": get_parameter("consider_depots", content, errors, optional=True),
        "pheromone_uses_first_hour": get_parameter("pheromone_uses_first_hour", content, errors, optional=True),
        "range_n_iterations": get_parameter("range_n_iterations", content, errors, optional=True),
        "range_n_sub_iterations": get_parameter("range_n_sub_iterations", content, errors, optional=True),
        "range_q": get_parameter("range_q", content, errors, optional=True),
        "range_alpha": get_parameter("range_alpha", content, errors, optional=True),
        "range_beta": get_parameter("range_beta", content, errors, optional=True),
        "range_rho": get_parameter("range_rho", content, errors, optional=True),
    }


def parse_common_tsp_parameters(content: dict, errors):
    return {
        "name": get_parameter("solutionName", content, errors),
        "auth": get_parameter("auth", content, errors, optional=True),
        "description": get_parameter("solutionDescription", content, errors),
        "locations": get_parameter("locations", content, errors, optional=True),
        "durations": get_parameter("durations", content, errors, optional=True),
        "locations_key": get_parameter("locationsKey", content, errors, optional=True),
        "durations_key": get_parameter("durationsKey", content, errors, optional=True),
        "customers": get_parameter("customers", content, errors),
        "start_node": get_parameter("startNode", content, errors),
        "start_time": get_parameter("startTime", content, errors),
        "do_loading_unloading": get_parameter("do_loading_unloading", content, errors),
        "cancel_customers": get_parameter("cancel_customers", content, errors),
    }


def parse_tsp_ga_parameters(content: dict, errors):
    return {
        "multi_threaded": get_parameter("multiThreaded", content, errors),
        "random_permutationCount": get_parameter("randomPermutationCount", content, errors),
        "iteration_count": get_parameter("iterationCount", content, errors),
    }


def parse_tsp_sa_parameters(content: dict, errors):
    return {
        "threshold": get_parameter("threshold", content, errors),
        "n_iterations": get_parameter("n_iterations", content, errors),
        "alpha": get_parameter("alpha", content, errors),
        "cooling": get_parameter("cooling", content, errors),
        "init": get_parameter("init", content, errors),
        "termination": get_parameter("termination", content, errors),
        "neighborhood": get_parameter("neighborhood", content, errors),
    }


def parse_tsp_aco_parameters(content: dict, errors):
    return {
        "n_hyperparams": get_parameter("n_hyperparams", content, errors),
        "aco_sols": get_parameter("aco_sols", content, errors, optional=True),
        "pheromone_uses_first_hour": get_parameter("pheromone_uses_first_hour", content, errors, optional=True),
        "range_n_iterations": get_parameter("range_n_iterations", content, errors, optional=True),
        "range_n_sub_iterations": get_parameter("range_n_sub_iterations", content, errors, optional=True),
        "range_q": get_parameter("range_q", content, errors, optional=True),
        "range_alpha": get_parameter("range_alpha", content, errors, optional=True),
        "range_beta": get_parameter("range_beta", content, errors, optional=True),
        "range_rho": get_parameter("range_rho", content, errors, optional=True),
    }
