from typing import Tuple
from supabase import create_client, Client

DATA_LOAD_FILE_PATH = "../../../data/loads/data_load.txt"


def get_content(file_path: str) -> Tuple[str, str]:
    file = open(file_path, "r")
    lines = file.readlines()
    for i in range(2):
        while lines[i][-1] == "\n":
            lines[i] = lines[i][:-1]
    return lines[0], lines[1]


def table_query(supabase: Client, table_name: str = "facts"):
    query = supabase.table(table_name).select("*").execute()
    print(query)
    print(query.data)
    print(len(query.data))


def list_files(supabase: Client, bucket_name: str = "image-bucket"):
    bucket_files = supabase.storage.from_(bucket_name).list()
    print(bucket_files)


def download_file(supabase: Client):
    with open("icardi.jpeg", "wb+") as f:
        response = supabase.storage.from_("image-bucket").download("icardi.jpeg")
        f.write(response)
        # print(response)


def upload_file(supabase: Client):
    with open(DATA_LOAD_FILE_PATH, "rb") as f:
        response = supabase.storage.from_("image-bucket").upload(
            file=f, path="data_load.txt", file_options={"content-type": "text/html"}
        )
        # print(response)


def run():
    url, key = get_content("supabase_url_key.txt")
    email, password = get_content("supabase_user.txt")
    supabase = create_client(url, key)
    # user = supabase.auth.sign_up({"email": email, "password": password})
    """
    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
    print(session)
    print(session.session.access_token)
    supabase.postgrest.auth(session.session.access_token)
    supabase.auth.sign_out()
    """
    table_query(supabase)
    download_file(supabase)
    upload_file(supabase)
    list_files(supabase)


if __name__ == "__main__":
    run()
