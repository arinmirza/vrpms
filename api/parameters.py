from api.helpers import get_parameter


def parse_common_parameters(content: dict, errors):
    return {
        'name': get_parameter('solutionName', content, errors),
        'auth': get_parameter('auth', content, errors, optional=True),
        'description': get_parameter('solutionDescription', content, errors),
        'locations_key': get_parameter('locationsKey', content, errors),
        'durations_key': get_parameter('durationsKey', content, errors),
        'capacities': get_parameter('capacities', content, errors),
        'ignoredCustomers': get_parameter('ignoredCustomers', content, errors),
        'completedCustomers': get_parameter('completedCustomers', content, errors),
    }


def parse_ga_parameters(content: dict, errors):
    return {
        'multiThreaded': get_parameter('multiThreaded', content, errors),
        'randomPermutationCount': get_parameter('randomPermutationCount', content, errors),
        'iterationCount': get_parameter('iterationCount', content, errors),
    }


def parse_sa_parameters(content: dict, errors):
    return {}


def parse_ant_parameters(content: dict, errors):
    return {}
