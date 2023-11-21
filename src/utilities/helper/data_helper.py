from typing import List, Optional, Tuple

from src.utilities.data_gen.based.data_gen import get_time_data
from src.db.supabase.db_supabase_mapbox import get_mapbox_duration_data, get_mapbox_locations_data, get_mapbox_load_data


def multiply_duration(duration: List[List[List[float]]], mult: int = 60):
    n1, n2, n3 = len(duration), len(duration[0]), len(duration[0][0])
    for i1 in range(n1):
        for i2 in range(n2):
            for i3 in range(n3):
                duration[i1][i2][i3] *= mult
    return duration


def get_load_data(input_file_load: Optional[str], n: int) -> List[int]:
    """
    Reads required capacities of locations for a problem where the loads are unique

    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param n: Size of load data
    :return: Loads (required capacities) of locations
    """
    if input_file_load:
        input_file = open(input_file_load, "r")
        load = []
        for i, line in enumerate(input_file):
            values = line.split(" ")
            load.append(int(values[0]))
        load = load[:n]
    else:
        load = [0 if i == 0 else 1 for i in range(n)]
    return load


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


def get_subset_time_data(
    duration_old: List[List[List[float]]], n: int = 50, convert_matrix: bool = False
) -> List[List[List[float]]]:
    """
    Gets the subset of time data with a specific size

    :param duration_old: Entire time data
    :param n: Size of new data
    :param convert_matrix: Flag if first dimension of duration_old is t or not
    :return: Time data of NxNx12 to be worked on
    """
    duration = []
    for i in range(n):
        duration_src = []
        for j in range(n):
            duration_src_dest = []
            for t in range(12):
                value = duration_old[t][i][j] if convert_matrix else duration_old[i][j][t]
                duration_src_dest.append(value)
            duration_src.append(duration_src_dest)
        duration.append(duration_src)
    return duration


def get_google_and_load_data(
    input_files_time: List[str],
    input_file_load: Optional[str],
    n: int = 50,
) -> Tuple[List[List[List[float]]], List[int]]:
    """
    Reads max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations

    :param input_files_time: Paths to the input files including duration values for each hour of the day
    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param n: Number of locations to be fetched from the dataset
    :return: Max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations
    """
    duration_old = []
    for input_file_time in input_files_time:
        duration_hour = read_time_data(input_file_time)
        duration_old.append(duration_hour)
    duration = get_subset_time_data(duration_old, n, True)
    multiply_duration(duration, mult=60)
    load = get_load_data(input_file_load, n)
    return duration, load


def get_based_and_load_data(
    input_file_load: Optional[str],
    n: int = 50,
    per_km_time: float = 5,
) -> Tuple[List[List[List[float]]], List[int]]:
    """
    Gets max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations

    :param input_file_load: Path to the input file including loads (required capacities) of locations, set to None if
        load is not unique
    :param n: Number of locations to be fetched from the dataset
    :param per_km_time: Multiplier to calculate duration from distance in km
    :return: Max number of cycles and capacity of the vehicle, dynamic duration data, and loads of locations
    """
    duration_old = get_time_data(per_km_time=per_km_time)
    duration = get_subset_time_data(duration_old, n, False)
    multiply_duration(duration, mult=60)
    load = get_load_data(input_file_load, n)
    return duration, load


def get_mapbox_and_load_data(
    supabase_url: Optional[str],
    supabase_key: Optional[str],
    supabase_url_key_file: Optional[str],
    n: int = 25,
    durations_query_row_id: int = 1,
    locations_query_row_id: int = 2,
):
    duration_old = get_mapbox_duration_data(supabase_url, supabase_key, supabase_url_key_file, durations_query_row_id)
    duration = get_subset_time_data(duration_old, n, False)
    locations = get_mapbox_locations_data(supabase_url, supabase_key, supabase_url_key_file, locations_query_row_id)
    load = get_mapbox_load_data(locations, n)
    return duration, load


def get_mapbox_duration_locations_load(
    supabase_url: Optional[str],
    supabase_key: Optional[str],
    durations_query_row_id: int = 1,
    locations_query_row_id: int = 2,
    n: int = None,
):
    duration = get_mapbox_duration_data(supabase_url, supabase_key, None, durations_query_row_id)
    locations = get_mapbox_locations_data(supabase_url, supabase_key, None, locations_query_row_id)
    if n is None:
        n = len(duration)
    load = get_mapbox_load_data(locations, n)
    return duration, locations, load
