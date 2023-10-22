import json
from http.server import BaseHTTPRequestHandler

import src.solver
import src.utilities.helper

# Absolute import modules inside src folder
#from src.vrp.brute_force.brute_force_based import run
#from src.genetic_algorithm.genetic_algorithm import run as run_genetic_algorithm
from src.genetic_algorithm.genetic_algorithm_v4_single_core_fast import run as genetic_algorithm_sc_fast
from src.genetic_algorithm.genetic_algorithm_v5_single_core_fastest import run as genetic_algorithm_sc_fastest
from src.genetic_algorithm.genetic_algorithm_v6_multi_core_fast import run as genetic_algorithm_mc_fast


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Construct an example response
        body = {
            "vrp_solution": src.solver.solve_vrp_problem(),
            "travel_duration": src.solver.calculate_duration("Unity Beta", "Marienplatz"),
            "current_date": src.utilities.helper.get_current_date(),
            #"metes_solution": run(),
            "yusuf_solution_genetic_algorithm_all_cores": genetic_algorithm_mc_fast(multithreaded=True),
            "yusuf_solution_genetic_algorithm_single_core_fast": genetic_algorithm_sc_fast(multithreaded=False),
            "yusuf_solution_genetic_algorithm_single_core_fastest": genetic_algorithm_sc_fastest(multithreaded=False)

        }

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode("utf-8")

        # Write response body into handler
        self.wfile.write(encoded_body)

        return
