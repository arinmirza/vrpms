import json
from http.server import BaseHTTPRequestHandler
from api.tsp.database_tsp import DatabaseTSP
from api.helpers import fail, success
from api.tsp.parameters_tsp import parse_common_parameters, parse_ga_parameters


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Hi, this is the TSP Genetic Algorithm endpoint".encode('utf-8'))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get('Content-Length', 0))
        content_string = str(self.rfile.read(content_length).decode('utf-8'))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_parameters(content, errors)
        params_ga = parse_ga_parameters(content, errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # Retrieve data from database
        database = DatabaseTSP(params['auth'])
        locations = database.get_locations_by_id(params['locations_key'], errors)
        durations = database.get_durations_by_id(params['durations_key'], errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # TODO: Run algorithm
        result = {
            'duration': 0,
            'vehicle': [],
        }

        # Save results
        if params['auth']:
            database.save_solution(
                name=params['name'],
                description=params['description'],
                locations=locations,
                vehicle=result['vehicle'],
                duration=result['duration'],
                errors=errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # Respond
        success(self, result)
