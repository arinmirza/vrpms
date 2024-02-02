import os
from typing import List

import numpy as np

INPUT_FILE_PATH = "../../../../data/google_api/static/duration_50_1689674014_0.txt"
OUTPUT_FOLDER_PATH = "../../../../data/google_api/dynamic"
OUTPUT_FILE_NAME_PREFIX = "dynamic_duration"

MULTIPLIERS = [1.0, 1.2, 1.4, 1.6, 1.8, 1.4, 1.3, 1.4, 1.5, 1.6, 1.1, 1.0]
N_FORECAST_HOURS = len(MULTIPLIERS)
MU_DIVIDED_BY_SIGMA = 100
GLOBAL_TIME_MULTIPLIER = 0.6


def get_dynamic_duration(static_duration: List[List[float]], forecast_hours: int) -> List[List[float]]:
    """
    Static to dynamic conversion by multiply with some factors inspired from the traffic flow during a day

    :param static_duration: Duration matrix N by N in seconds for the first hour of the day
    :param forecast_hours: The hour (time slice) in [0, 12)
    :return: Duration matrix N by N in seconds for the given hour of the day
    """
    dynamic_duration = []
    n = len(static_duration)
    for i in range(n):
        dynamic_duration_src = []
        for j in range(n):
            if i == j:
                dynamic_duration_src.append(0)
            else:
                mu = static_duration[i][j] * MULTIPLIERS[forecast_hours]
                sigma = mu / MU_DIVIDED_BY_SIGMA
                seconds = float(np.random.normal(mu, sigma, 1)[0]) * GLOBAL_TIME_MULTIPLIER
                minutes = seconds / 60
                dynamic_duration_src.append(minutes)
        dynamic_duration.append(dynamic_duration_src)
    return dynamic_duration


def get_static_duration() -> List[List[float]]:
    """
    Gets duration matrix N by N in seconds for the first hour of the day

    :return: Duration matrix N by N in seconds for the first hour of the day
    """
    static_duration = []
    with open(INPUT_FILE_PATH) as file:
        lines = file.readlines()
        n = len(lines)
        for line in lines:
            static_duration_src = []
            content = line.split()
            for number in content:
                static_duration_src.append(float(number))
            static_duration.append(static_duration_src)
    return static_duration


def output_file(dynamic_duration: List[List[float]], forecast_hours: int) -> None:
    """
    Saves duration matrix for the given hour of the day as integers and floating numbers

    :param dynamic_duration: Duration matrix N by N in seconds for the given hour of the day
    :param forecast_hours: The hour (time slice) in [0, 12)
    """
    os.makedirs(f"{OUTPUT_FOLDER_PATH}/float/", exist_ok=True)
    output_file_name = f"{OUTPUT_FOLDER_PATH}/float/{OUTPUT_FILE_NAME_PREFIX}_float_{forecast_hours}.txt"
    with open(output_file_name, "w") as file:
        file.writelines(" ".join(str(float(j)) for j in i) + "\n" for i in dynamic_duration)
    os.makedirs(f"{OUTPUT_FOLDER_PATH}/int/", exist_ok=True)
    output_file_name = f"{OUTPUT_FOLDER_PATH}/int/{OUTPUT_FILE_NAME_PREFIX}_int_{forecast_hours}.txt"
    with open(output_file_name, "w") as file:
        file.writelines(" ".join(str(int(j)) for j in i) + "\n" for i in dynamic_duration)


def run() -> None:
    """
    Calculates and saves duration matrix for all hours in [0, 12)
    """
    static_duration = get_static_duration()
    for forecast_hours in range(N_FORECAST_HOURS):
        dynamic_duration = get_dynamic_duration(static_duration, forecast_hours)
        output_file(dynamic_duration, forecast_hours)


if __name__ == "__main__":
    run()
