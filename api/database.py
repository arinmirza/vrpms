import os
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions

class Database:
    # _url: str = os.environ.get('SUPABASE_URL') or ''
    # _key: str = os.environ.get('SUPABASE_KEY') or ''
    _url = "https://pkeygmzuwfucblldmkjn.supabase.co"
    _key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s"
    client: Client

    def __init__(self, auth=None):
        '''Create supabase client using anonymous url and key.'''
        self.client = create_client(self._url, self._key, options=ClientOptions(persist_session=False))
        if auth:
            self.login(auth)


    def login(self, token: str):
        '''Login with the JWT token of a specific user.'''
        self.client.auth.set_session(access_token=token, refresh_token=token)


    def get_locations_by_id(self, id, errors):
        try:
            result = self.client.table('locations').select('*').eq('id', id).execute()
            if not len(result.data):
                raise(Exception(f'No location set found with given id {id}'))
            return result.data[0]
        except Exception as exception:
            errors += [{ 'what': 'Database read error', 'reason': str(exception)}]
            return None


    def get_durations_by_id(self, id, errors):
        try:
            result = self.client.table('durations').select('*').eq('id', id).execute()
            if not len(result.data):
                raise(Exception(f'No duration matrix found with given id {id}'))
            return result.data[0]
        except Exception as exception:
            errors += [{ 'what': 'Database read error', 'reason': str(exception)}]
            return None
        
    
    def save_solution(self, name, description, locations, vehicles, durationMax, durationSum, errors):
        user = self.client.auth.get_user()
        email = user.model_dump()['user']['email'] if user else None

        # This error message is only for information purposes, and the actual security is enforced by
        # row level policies of the postgres database. Still, the email string taken from the JWT
        # cannot be tampered with as the token is securely validated by Supabase.
        if not email:
            errors += [{
                'what': 'Not permitted', 
                'reason': 'An authentication token is required to save solutions to database.' + \
                    " Please provide 'auth' with a valid JWT token in the request body"
            }]
            return
            
        data = {
            'name': name,
            'description': description,
            'owner': email,
            'durationMax': durationMax,
            'durationSum': durationSum,
            'locations': locations,
            'vehicles': vehicles,
        }

        try:
            return self.client.table('solutions').insert(data).execute()
        except Exception as exception:
            errors += [{ 'what': 'Database write error', 'reason': str(exception)}]