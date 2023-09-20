import json
from http.server import BaseHTTPRequestHandler

# Absolute import modules inside src folder
import src.utilities.today
import src.utilities.foo
import src.solver

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Construct an example response 
        body = {
            'vrp_solution': src.solver.solve_vrp_problem(),
            'travel_duration': src.solver.calculate_duration("Unity Beta", "Marienplatz"),
            'current_date': src.utilities.today.get_current_date(),
        }
        
        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode('utf-8')

        # Write response body into handler
        self.wfile.write(encoded_body)
        
        return
