import json
from http.server import BaseHTTPRequestHandler

import api.src.solver
import api.src.utilities.today

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Construct an example response 
        body = {
            'vrp_solution': api.src.solver.solve_vrp_problem(),
            'travel_duration': api.src.solver.calculate_duration("Unity Beta", "Marienplatz"),
            'current_date': api.src.utilities.today.get_current_date(),
        }

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode('utf-8')

        # Write response body into handler
        self.wfile.write(encoded_body)
        
        return
