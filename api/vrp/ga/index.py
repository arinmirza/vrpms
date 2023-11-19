import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseVRP
from api.helpers import fail, success
from api.parameters import parse_common_vrp_parameters, parse_vrp_ga_parameters
from src.genetic_algorithm.genetic_algorithm import run_GA as run

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Genetic Algorithm endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_vrp_parameters(content, errors)
        params_ga = parse_vrp_ga_parameters(content, errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # Retrieve data from database
        database = DatabaseVRP(params["auth"])
        locations = database.get_locations_by_id(params["locations_key"], errors)
        durations = database.get_durations_by_id(params["durations_key"], errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # TODO: Run algorithm
        result = run(locations=locations, durations=durations, initial_start_times=params["start_times"],
            capacities=params["capacities"], ignored_customers=params["ignored_customers"],
            completed_customers=params["completed_customers"],start_node=None, mode="TDVRP",  multithreaded=params_ga["multi_threaded"], iteration_count=0,random_perm_count=0)
        #result = {
        #    "durationMax": 0,
        #    "durationSum": 0,
        #    "vehicles": [],
        #}

        # Save results
        if params["auth"]:
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=locations,
                vehicles=result["vehicles"],
                duration_max=result["durationMax"],
                duration_sum=result["durationSum"],
                errors=errors,
            )

        if len(errors) > 0:
            fail(self, errors)
            return

        # Respond
        success(self, result)
