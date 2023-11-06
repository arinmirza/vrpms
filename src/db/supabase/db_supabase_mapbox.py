from typing import List, Tuple
from supabase import create_client, Client

SUPABASE_URK_KEY_FILE = "../../../data/supabase/supabase_url_key.txt"


def get_content(file_path: str) -> Tuple[str, str]:
    file = open(file_path, "r")
    lines = file.readlines()
    for i in range(2):
        while lines[i][-1] == "\n":
            lines[i] = lines[i][:-1]
    return lines[0], lines[1]


def table_query(supabase: Client, table_name: str = "durations") -> List[List[float]]:
    query = supabase.table(table_name).select("*").execute()
    mapbox_data = query.data[0]["json"]
    return mapbox_data


def run():
    url, key = get_content(SUPABASE_URK_KEY_FILE)
    supabase = create_client(url, key)
    mapbox_data = table_query(supabase)
    print(mapbox_data)


if __name__ == "__main__":
    run()
