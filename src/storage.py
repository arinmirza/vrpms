import os
from supabase.client import create_client, Client


#url: str = os.environ.get("https://pvekgkfwzkklidborsbt.supabase.co")
#key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2ZWtna2Z3emtrbGlkYm9yc2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTAzMDQ4NjIsImV4cCI6MjAwNTg4MDg2Mn0.VKy-CU7ars-kbha95TSoN-KFFbZcaBhAB1Y75CpShM8")

url = "https://pvekgkfwzkklidborsbt.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2ZWtna2Z3emtrbGlkYm9yc2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTAzMDQ4NjIsImV4cCI6MjAwNTg4MDg2Mn0.VKy-CU7ars-kbha95TSoN-KFFbZcaBhAB1Y75CpShM8"

supabase: Client = create_client(supabase_url=url, supabase_key=key)


def upload_sample_file():
    #with open('../requirements.txt', 'rb') as file:

    #res = supabase.storage.from_('bucket').download(file=file, path='my-requirements.txt')
    print("Download completed")
    print("Response:", res)


if __name__ == '__main__':
    upload_sample_file()