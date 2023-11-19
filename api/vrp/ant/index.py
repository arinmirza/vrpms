import json
from http.server import BaseHTTPRequestHandler
from api.database import Database
from api.helpers import fail, success
from api.parameters import parse_common_parameters
from api.parameters import parse_ant_parameters

class handler(BaseHTTPRequestHandler):


    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Ant Colony Optimization endpoint".encode('utf-8'))
        
    
    def do_POST(self):
        # Read
        content_length = int(self.headers.get('Content-Length', 0))
        content_string = str(self.rfile.read(content_length).decode('utf-8'))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_parameters(content, errors)
        params_ga = parse_ant_parameters(content, errors)

        if len(errors) > 0:
            fail(self, errors)
            return
        
        # Retrieve data from database
        database = Database(params['auth'])
        locations = database.get_locations_by_id(params['locations_key'], errors)
        durations = database.get_durations_by_id(params['durations_key'], errors)

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
            name=params['name'], 
            description=params['description'], 
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