import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseVRP
from api.helpers import fail, success
from api.parameters import parse_common_vrp_parameters
from src.vehicles_priority_queue.brute_force_old.brute_force import run_request
from src.utilities.utilities1.helper import convert_locations, get_demand_data_from_locations
from src.utilities.utilities1.helper import vrp_result_2_output


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Brute Force endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_vrp_parameters(content, errors)

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

        locations = convert_locations(locations)
        demands = get_demand_data_from_locations(durations, locations)
        vrp_result = run_request(
            q=params["capacities"][0],
            ignore_long_trip=False,
            duration=durations,
            load=demands,
            ignored_customers=params["ignored_customers"],
            completed_customers=params["completed_customers"],
            vehicles_start_times=params["start_times"],
            locations=locations,
            objective_func_type="min_sum_time",
        )
        result = vrp_result_2_output(
            vehicles_start_times=params["start_times"],
            duration=durations,
            locations=locations,
            vrp_result=vrp_result,
            capacities=params["capacities"],
        )

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
