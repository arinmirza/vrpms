import os
from api.database import Database
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions


class DatabaseVRP(Database):

    def save_solution(self, name, description, locations, vehicles, duration_max, duration_sum, errors):
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
            'durationMax': duration_max,
            'durationSum': duration_sum,
            'locations': locations,
            'vehicles': vehicles,
        }

        try:
            return self.client.table('solutions').insert(data).execute()
        except Exception as exception:
            errors += [{ 'what': 'Database write error', 'reason': str(exception)}]
