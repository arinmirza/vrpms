import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseVRP
from api.helpers import fail, success
from api.parameters import parse_common_vrp_parameters, parse_vrp_ga_parameters
from src.genetic_algorithm.genetic_algorithm import run_GA as run
from api.helpers import remove_unused_locations
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Genetic Algorithm endpoint".encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

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
        if "locations" not in params and "locations_key" not in params:
            errors += [{"what": "Missing parameter", "reason": "locations or locationsKey should be provided"}]
        if "durations" not in params and "durations_key" not in params:
            errors += [{"what": "Missing parameter", "reason": "durations or durationsKey should be provided"}]

        if len(errors) > 0:
            fail(self, errors)
            return

        # Retrieve data from database
        database = DatabaseVRP(params["auth"])
        locations = (
            params["locations"]
            if "locations" in params and params["locations"] is not None
            else database.get_locations_by_id(params["locations_key"], errors)
        )
        durations = (
            params["durations"]
            if "durations" in params and params["durations"] is not None
            else database.get_durations_by_id(params["durations_key"], errors)
        )

        if len(errors) > 0:
            fail(self, errors)
            return

        # Run the algorithm
        result = run(locations=locations,
                     durations=durations,
                     initial_start_times=params["start_times"],
                     capacities=params["capacities"],
                     ignored_customers=params["ignored_customers"],
                     completed_customers=params["completed_customers"],
                     start_node=None,
                     mode="TDVRP",
                     multithreaded=params_ga["multi_threaded"],
                     iteration_count=params_ga["iteration_count"],
                     random_perm_count=params_ga["random_permutationCount"],
                     customers=None,
                     cancelled_customers=[],
                     do_load_unload=False,
                     max_k=params_ga["max_k"] if params_ga["max_k"] != None else -1 ,
                     k_lower_limit=params_ga["k_lower_limit"] if params_ga["k_lower_limit"] != None else True)

        # Save results
        if params["auth"]:
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=remove_unused_locations(locations, params["ignored_customers"], params["completed_customers"]),
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
