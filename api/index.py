import json
from http.server import BaseHTTPRequestHandler

#from src.example_folder import bar
#from src.foo import solve_vrp_problem
#from src.foo import calculate_duration


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Construct an example response 
        #body = {
        #    'vrp_solution': solve_vrp_problem(),
        #    'travel_duration': calculate_duration("Unity Beta", "Marienplatz"),
        #    'current_date': bar.get_current_date(),
        #}

        body = { 'Hello': 'World!'}

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode('utf-8')

        # Write response body into handler
        self.wfile.write(encoded_body)
        
        return
