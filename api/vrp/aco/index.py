import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseVRP
from api.helpers import fail, success
from api.parameters import parse_common_vrp_parameters, parse_vrp_aco_parameters
from src.vrp.ant_colony.aco_hybrid import run_request
from src.utilities.helper.locations_helper import (
    convert_locations,
    get_available_and_all_ignored_customers,
    get_demands_from_locations,
)
from src.utilities.helper.result_2_output import vrp_result_2_output


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Ant Colony Optimization endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_vrp_parameters(content, errors)
        params_aco = parse_vrp_aco_parameters(content, errors)

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

        new_locations = convert_locations(locations)
        available_customers, all_ignored_customers = get_available_and_all_ignored_customers(
            locations=new_locations,
            ignored_customers=params["ignored_customers"],
            completed_customers=params["completed_customers"],
        )
        demands = get_demands_from_locations(durations, new_locations)

        vrp_result = run_request(
            q=params["capacities"][0],
            duration=durations,
            load=demands,
            available_customers=available_customers,
            vehicles_start_times=params["start_times"],
            n_hyperparams=params_aco["n_hyperparams"],
        )
        result = vrp_result_2_output(
            vehicles_start_times=params["start_times"],
            duration=durations,
            locations=new_locations,
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
