from random import randint, shuffle

from src.utilities.helper.date_helper import get_current_date


def calculate_duration(source: str, target: str, time_of_day: int = 0):
    """Given a source address and a target address, calculates the travel duration.
    Optionally, time of day can be specified for this calculation."""

    # Generate a duration in minutes
    duration = randint(3, 320)

    # Return the calculated duration as a dictionary
    return {
        "source": source,
        "target": target,
        "duration": duration,
        "units": "minutes",
    }


def solve_vrp_problem():
    """Solves the VRP problem, and returns tour and additional information."""

    # Generate a random tour
    tour = list(range(1, 15))
    shuffle(tour)
    tour = [0] + tour + [0]

    # Return the tour and total
    return {
        "tour": tour,
        "total_time": 150,
        "unvisited": [],
        "date": get_current_date(),
    }
