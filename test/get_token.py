from supabase.client import create_client, Client

# Set login credentials
URL: str = "https://pkeygmzuwfucblldmkjn.supabase.co"
KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s"
EMAIL: str = "yusufserdar1700@gmail.com"
PASSWORD: str = "yusufgym123!"

# Connect and login
supabase: Client = create_client(URL, KEY)
supabase.auth.sign_in_with_password({ 'email': EMAIL, 'password': PASSWORD })
session = supabase.auth.get_session()

# Print tokens
if session:
    access_token = session.access_token
    refresh_token = session.refresh_token
    print('access_token:', access_token)