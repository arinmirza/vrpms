from api.helpers import get_parameter


def parse_common_parameters(content: dict, errors):
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


def parse_ga_parameters(content: dict, errors):
    return {}


def parse_sa_parameters(content: dict, errors):
    return {}


def parse_aco_parameters(content: dict, errors):
    return {}
