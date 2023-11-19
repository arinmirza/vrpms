import json
from http.server import BaseHTTPRequestHandler
from api.database import Database
from api.helpers import get_parameter, fail, success

class handler(BaseHTTPRequestHandler):


    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Hi, this is /vrp/ga endpoint".encode('utf-8'))
        
    
    def do_POST(self):
        # Read
        content_length = int(self.headers.get('Content-Length', 0))
        content_string = str(self.rfile.read(content_length).decode('utf-8'))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        name = get_parameter('solutionName', content, errors)
        description = get_parameter('solutionDescription', content, errors)
        locations_key = get_parameter('locationsKey', content, errors)
        durations_key = get_parameter('durationsKey', content, errors)
        capacities = get_parameter('capacities', content, errors)
        ignoredCustomers = get_parameter('ignoredCustomers', content, errors)
        completedCustomers = get_parameter('completedCustomers', content, errors)
        multiThreaded = get_parameter('multiThreaded', content, errors)
        randomPermutationCount = get_parameter('randomPermutationCount', content, errors)
        iterationCount = get_parameter('iterationCount', content, errors)
        auth = get_parameter('auth', content, errors, optional=True)

        if len(errors) > 0:
            fail(self, errors)
            return
        
        # Retrieve data from database
        database = Database(auth)
        locations = database.get_locations_by_id(locations_key, errors)
        durations = database.get_durations_by_id(durations_key, errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # TODO: Run algorithm
        result = {
            'durationMax': 0,
            'durationSum': 0,
            'vehicles': [],
        }

        # Save results
        database.save_solution(
            name=name, 
            description=description, 
            locations=locations, 
            vehicles=result['vehicles'],
            durationMax=result['durationMax'],
            durationSum=result['durationSum'],
            errors=errors)
        
        if len(errors) > 0:
            fail(self, errors)
            return

        # Respond
        success(self)
        


