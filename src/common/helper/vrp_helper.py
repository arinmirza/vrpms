from typing import List, Tuple, Optional
from src.common.data_gen.based.data_gen import get_time_data


def read_time_data(input_file_time: str) -> List[List[float]]:
    """
    Reads a matrix of duration data for a specific hour

    :param input_file_time: Path to the input file including duration values
    :return: Matrix of duration data for a specific hour
    """
    input_file = open(input_file_time, "r")
    duration = []
    for i, line in enumerate(input_file):
        values = line.split(" ")
        duration_src = []
        for value in values:
            duration_src.append(float(value))
        duration.append(duration_src)
    return duration


def read_load_data(input_file_load: str) -> List[int]:
    """
    Reads required capacities of locations for a problem where the loads are unique

    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :return: Loads (required capacities) of locations
    """
    input_file = open(input_file_load, "r")
    load = []
    for i, line in enumerate(input_file):
        values = line.split(" ")
        load.append(int(values[0]))
    return load


def get_google_and_load_data(input_files_time: List[str], input_file_load: Optional[str], n: int = 50,
                             convert_matrix: bool = False) -> Tuple[List[List[List[float]]], List[int]]:
    """
    Reads max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations

    :param input_files_time: Paths to the input files including duration values for each hour of the day
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param n: Number of locations to be fetched from the dataset
    :param convert_matrix: Flag to convert duration matrix from 12xNxN to NxNx12
    :return: Max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations
    """
    duration_old = []
    for input_file_time in input_files_time:
        duration_hour = read_time_data(input_file_time)
        duration_old.append(duration_hour)
    duration = []
    for t in range(12):
        duration_t = []
        for i in range(n):
            duration_t.append(duration_old[t][i][:n])
        duration.append(duration_t)
    if input_file_load:
        load = read_load_data(input_file_load)
        load = load[:n]
    else:
        load = [0 if i == 0 else 1 for i in range(n)]
    if convert_matrix:
        duration = convert_duration(n, duration)
    return duration, load


def get_based_and_load_data(input_file_load: Optional[str], n: int = 50, per_km_time: float = 5,
                            convert_matrix: bool = False) -> Tuple[List[List[List[float]]], List[int]]:
    """
    Gets max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations

    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param n: Number of locations to be fetched from the dataset
    :param per_km_time: Multiplier to calculate duration from distance in km
    :param convert_matrix: Flag to convert duration matrix from 12xNxN to NxNx12
    :return: Max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations
    """
    duration_old = get_time_data(per_km_time=per_km_time)
    duration = []
    for t in range(12):
        duration_t = []
        for i in range(n):
            duration_t_src = []
            for j in range(n):
                duration_t_src.append(duration_old[i][j][t])
            duration_t.append(duration_t_src)
        duration.append(duration_t)
    if input_file_load:
        load = read_load_data(input_file_load)
        load = load[:n]
    else:
        load = [0 if i == 0 else 1 for i in range(n)]
    if convert_matrix:
        duration = convert_duration(n, duration)
    return duration, load


def convert_duration(n: int, duration_old: List[List[List[float]]]) -> List[List[List[float]]]:
    """
    Converts duration matrix from 12xNxN to NxNx12

    :param n: Number of locations to be fetched from the dataset
    :param duration_old: 12xNxN duration matrix
    :return: NxNx12 duration matrix
    """
    duration = []
    for i in range(n):
        duration_src = []
        for j in range(n):
            duration_src_dest = []
            for t in range(12):
                duration_src_dest.append(duration_old[t][i][j])
            duration_src.append(duration_src_dest)
        duration.append(duration_src)
    return duration
