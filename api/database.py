import os
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions


class Database:
    _url: str = os.environ.get("SUPABASE_URL") or "https://pkeygmzuwfucblldmkjn.supabase.co"
    _key: str = (
        os.environ.get("SUPABASE_KEY")
        or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s"
    )
    client: Client

    def __init__(self, auth=None):
        """Create supabase client using anonymous url and key."""
        self.client = create_client(self._url, self._key, options=ClientOptions(persist_session=False))
        if auth:
            self.login(auth)

    def login(self, token: str):
        """Login with the JWT token of a specific user."""
        try:
            self.client.auth.set_session(access_token=token, refresh_token=token)
        except:
            pass

    def get_locations_by_id(self, id, errors, table_name="locations", column_name="locations"):
        try:
            result = self.client.table(table_name).select("*").eq("id", id).execute()
            if not len(result.data):
                raise (Exception(f"No location set found with given id {id}"))
            return result.data[0][column_name]
        except Exception as exception:
            errors += [{"what": "Database read error", "reason": str(exception)}]
            return None

    def get_durations_by_id(self, id, errors, table_name="durations", column_name="matrix"):
        try:
            result = self.client.table(table_name).select("*").eq("id", id).execute()
            if not len(result.data):
                raise (Exception(f"No duration matrix found with given id {id}"))
            return result.data[0][column_name]
        except Exception as exception:
            errors += [{"what": "Database read error", "reason": str(exception)}]
            return None


class DatabaseVRP(Database):
    def save_solution(self, name, description, locations, vehicles, duration_max, duration_sum, errors):
        user = self.client.auth.get_user()
        email = user.model_dump()["user"]["email"] if user else None

        # This error message is only for information purposes, and the actual security is enforced by
        # row level policies of the postgres database. Still, the email string taken from the JWT
        # cannot be tampered with as the token is securely validated by Supabase.
        if not email:
            errors += [
                {
                    "what": "Not permitted",
                    "reason": "An authentication token is required to save solutions to database."
                    + " Please provide 'auth' with a valid JWT token in the request body",
                }
            ]
            return

        data = {
            "name": name,
            "description": description,
            "owner": email,
            "durationMax": duration_max,
            "durationSum": duration_sum,
            "locations": locations,
            "vehicles": vehicles,
        }

        try:
            return self.client.table("solutions").insert(data).execute()
        except Exception as exception:
            errors += [{"what": "Database write error", "reason": str(exception)}]


class DatabaseTSP(Database):
    def save_solution(self, name, description, locations, vehicles, duration, errors):
        user = self.client.auth.get_user()
        email = user.model_dump()["user"]["email"] if user else None

        # This error message is only for information purposes, and the actual security is enforced by
        # row level policies of the postgres database. Still, the email string taken from the JWT
        # cannot be tampered with as the token is securely validated by Supabase.
        if not email:
            errors += [
                {
                    "what": "Not permitted",
                    "reason": "An authentication token is required to save solutions to database."
                    + " Please provide 'auth' with a valid JWT token in the request body",
                }
            ]
            return

        data = {
            "name": name,
            "description": description,
            "owner": email,
            "durationMax": duration,
            "durationSum": duration,
            "locations": locations,
            "vehicles": vehicles,
        }

        try:
            return self.client.table("solutions").insert(data).execute()
        except Exception as exception:
            errors += [{"what": "Database write error", "reason": str(exception)}]
