import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseTSP
from api.helpers import fail, success
from api.parameters import parse_common_tsp_parameters, parse_tsp_ga_parameters
from src.genetic_algorithm.genetic_algorithm import run_GA as run
from api.helpers import remove_unused_locations_tsp

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the TSP Genetic Algorithm endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_tsp_parameters(content, errors)
        params_ga = parse_tsp_ga_parameters(content, errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # Retrieve data from database
        database = DatabaseTSP(params["auth"])
        locations = database.get_locations_by_id(params["locations_key"], errors)
        durations = database.get_durations_by_id(params["durations_key"], errors)

        if len(errors) > 0:
            fail(self, errors)
            return

        # TODO: Run algorithm
        result = run(locations=locations,
                     durations=durations,
                     initial_start_times=params["start_time"],
                     capacities=None,
                     ignored_customers=None,
                     completed_customers=None,
                     start_node=params["start_node"],
                     mode="TSP",
                     multithreaded=params_ga["multi_threaded"],
                     customers=params["customers"],
                     iteration_count=0,
                     random_perm_count=0)

        # TODO: Run algorithm
        #result = {
        #    "duration": 0,
        #    "vehicle": [],
        #}

        # Save results
        if params["auth"]:
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=remove_unused_locations_tsp(locations=locations, customers=params["customers"],
                                                      start_node=params, depot=0),
                vehicle=result["vehicles"],
                duration_max=result["durationMax"],
                duration_sum=result["durationSum"],
                errors=errors,
            )

        if len(errors) > 0:
            fail(self, errors)
            return

        # Respond
        success(self, result)
