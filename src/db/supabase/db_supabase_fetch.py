from typing import Tuple
from supabase import create_client, Client


def get_supabase_url_key(file_path: str) -> Tuple[str, str]:
    file = open(file_path, "r")
    lines = file.readlines()
    url, key = lines[0], lines[1]
    while url[-1] == '\n':
        url = url[:-1]
    while key[-1] == '\n':
        key = key[:-1]
    return url, key


def run():
    url, key = get_supabase_url_key("supabase_url_key.txt")
    supabase: Client = create_client(url, key)
    table_query = supabase.table("facts").select("*").execute()
    print(table_query)
    print(table_query.data)
    print(len(table_query.data))


if __name__ == "__main__":
    run()
