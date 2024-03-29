from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client

DEPOT = 0


def get_url_key(file_path: str) -> Tuple[str, str]:
    file = open(file_path, "r")
    lines = file.readlines()
    for i in range(2):
        while lines[i][-1] == "\n":
            lines[i] = lines[i][:-1]
    return lines[0], lines[1]


def get_supabase_client(
    url: Optional[str] = None,
    key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
):
    if supabase_url_key_file:
        url, key = get_url_key(supabase_url_key_file)
    supabase_client = create_client(url, key)
    return supabase_client


def get_mapbox_duration_data(
    url: Optional[str] = None,
    key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    query_row_id: int = 1,
    table_name: str = "durations",
    query_column_name: str = "id",
    data_column_name: str = "matrix",
):
    supabase_client = get_supabase_client(url, key, supabase_url_key_file)
    query = supabase_client.table(table_name).select("*").eq(column=query_column_name, value=query_row_id).execute()
    mapbox_data = query.data[0][data_column_name]
    # print(mapbox_data)
    return mapbox_data


def get_mapbox_locations_data(
    url: Optional[str] = None,
    key: Optional[str] = None,
    supabase_url_key_file: Optional[str] = "../../../data/supabase/supabase_url_key.txt",
    query_row_id: int = 2,
    table_name: str = "locations",
    query_column_name: str = "id",
    data_column_name: str = "locations",
):
    supabase_client = get_supabase_client(url, key, supabase_url_key_file)
    query = supabase_client.table(table_name).select("*").eq(column=query_column_name, value=query_row_id).execute()
    mapbox_data = query.data[0][data_column_name]
    # print(mapbox_data)
    locations = {}
    for location in mapbox_data:
        locations[location["id"]] = location
    # print(locations)
    return locations


def get_mapbox_load_data(locations: Dict, n: int = 25):
    load = [0 for _ in range(n)]
    for key, customer in locations.items():
        id, demand = customer["id"], customer["demand"]
        if DEPOT < id < n:
            load[id] = demand
    # print(load)
    return load


if __name__ == "__main__":
    duration = get_mapbox_duration_data()
    locations = get_mapbox_locations_data()
    n = len(duration)
    load = get_mapbox_load_data(locations, n)
    print(duration)
    print(locations)
    print(load)
