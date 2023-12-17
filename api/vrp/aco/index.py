import datetime
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
    remove_unused_locations_vrp,
)
from src.utilities.helper.result_2_output import vrp_result_2_output


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Ant Colony Optimization endpoint".encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
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
        params_aco = parse_vrp_aco_parameters(content, errors)

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

        time_start = datetime.datetime.now()

        new_locations = convert_locations(locations)
        available_customers, all_ignored_customers = get_available_and_all_ignored_customers(
            locations=new_locations,
            ignored_customers=params["ignored_customers"],
            completed_customers=params["completed_customers"],
        )
        demands = get_demands_from_locations(durations, new_locations)
        filtered_locations = remove_unused_locations_vrp(
            locations, params["ignored_customers"], params["completed_customers"]
        )

        vrp_result = run_request(
            q=params["capacities"][0],
            duration=durations,
            load=demands,
            available_customers=available_customers,
            vehicles_start_times=params["start_times"],
            n_hyperparams=params_aco["n_hyperparams"],
            aco_sols=params["aco_sols"],
            consider_depots=params["consider_depots"],
            pheromone_uses_first_hour=params["pheromone_uses_first_hour"],
            range_n_iterations=params["range_n_iterations"],
            range_n_sub_iterations=params["range_n_sub_iterations"],
            range_q=params["range_q"],
            range_alpha=params["range_alpha"],
            range_beta=params["range_beta"],
            range_rho=params["range_rho"],
        )
        result = vrp_result_2_output(
            vehicles_start_times=params["start_times"],
            duration=durations,
            load=demands,
            locations=new_locations,
            vrp_result=vrp_result,
            capacities=params["capacities"],
        )

        time_end = datetime.datetime.now()
        time_diff = (time_end - time_start).total_seconds()
        result["time_diff"] = time_diff

        # Save results
        if params["auth"]:
            duration_max = int(result["durationMax"])
            duration_sum = int(result["durationSum"])
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=filtered_locations,
                vehicles=result["vehicles"],
                duration_max=duration_max,
                duration_sum=duration_sum,
                errors=errors,
            )

        if errors:
            result["errors"] = errors

        # Respond
        success(self, result)
