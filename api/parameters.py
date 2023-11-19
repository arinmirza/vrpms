from api.helpers import get_parameter


def parse_common_vrp_parameters(content: dict, errors):
    return {
        'name': get_parameter('solutionName', content, errors),
        'auth': get_parameter('auth', content, errors, optional=True),
        'description': get_parameter('solutionDescription', content, errors),
        'locations_key': get_parameter('locationsKey', content, errors),
        'durations_key': get_parameter('durationsKey', content, errors),
        'capacities': get_parameter('capacities', content, errors),
        'start_times': get_parameter('startTimes', content, errors),
        'ignored_customers': get_parameter('ignoredCustomers', content, errors),
        'completed_customers': get_parameter('completedCustomers', content, errors),
    }


def parse_vrp_ga_parameters(content: dict, errors):
    return {
        'multi_threaded': get_parameter('multiThreaded', content, errors),
        'random_permutationCount': get_parameter('randomPermutationCount', content, errors),
        'iteration_count': get_parameter('iterationCount', content, errors),
    }


def parse_vrp_sa_parameters(content: dict, errors):
    return {}


def parse_vrp_aco_parameters(content: dict, errors):
    return {}


def parse_common_tsp_parameters(content: dict, errors):
    return {
        'name': get_parameter('solutionName', content, errors),
        'auth': get_parameter('auth', content, errors, optional=True),
        'description': get_parameter('solutionDescription', content, errors),
        'locations_key': get_parameter('locationsKey', content, errors),
        'durations_key': get_parameter('durationsKey', content, errors),
        'customers': get_parameter('customers', content, errors),
        'start_node': get_parameter('startNode', content, errors),
        'start_time': get_parameter('startTime', content, errors),
    }


def parse_tsp_ga_parameters(content: dict, errors):
    return {}


def parse_tsp_sa_parameters(content: dict, errors):
    return {}


def parse_tsp_aco_parameters(content: dict, errors):
    return {}
