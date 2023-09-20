import json
from http.server import BaseHTTPRequestHandler

#import src.solver
#import src.utilities.today

import os
import src.utilities.today
import src.utilities.foo
#import src.solver

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Construct an example response 
        #body = {
        #    'vrp_solution': src.solver.solve_vrp_problem(),
        #    'travel_duration': src.solver.calculate_duration("Unity Beta", "Marienplatz"),
        #    'current_date': src.utilities.today.get_current_date(),
        #}

        body = {
            'today': src.utilities.today.get_current_date(),
            #'solver': src.solver.get_current_date(),
            'foo': src.utilities.foo.print_info(),
            'cwd': os.getcwd(),
            'cwd_content': os.listdir(os.getcwd()),
            'parent': os.path.dirname(os.getcwd()),
            'parent_content': os.listdir(os.path.dirname(os.getcwd())),
        }

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode('utf-8')

        # Write response body into handler
        self.wfile.write(encoded_body)
        
        return
