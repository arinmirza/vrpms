import os
from supabase import create_client, Client
from src.supabase_help.get_supabase_matrix import get_data

def get_supabase_matrix():
  url: str = os.environ.get("SUPABASE_URL")
  key: str = os.environ.get("SUPABASE_KEY")

  supabase: Client = create_client(url, key)

  with open("dataset_matrix.npy", 'wb+') as f:
    res = supabase.storage.from_('public/dataset').download("matrix.npy")
    f.write(res)


get_supabase_matrix()