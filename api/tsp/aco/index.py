import datetime
import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseTSP
from api.helpers import fail, success
from api.parameters import parse_common_tsp_parameters, parse_tsp_aco_parameters
from src.tsp.ant_colony.aco_hybrid import run_request
from src.utilities.helper.locations_helper import (
    convert_locations,
    remove_unused_locations_tsp,
    get_demands_from_locations,
)
from src.utilities.helper.result_2_output import tsp_result_2_output


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the TSP Ant Colony Optimization endpoint".encode("utf-8"))

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
        params = parse_common_tsp_parameters(content, errors)
        params_aco = parse_tsp_aco_parameters(content, errors)

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

        time_start = datetime.datetime.now()

        do_loading_unloading = params["do_loading_unloading"]
        cancel_customers = params["cancel_customers"]

        new_locations = convert_locations(locations)
        demands = get_demands_from_locations(durations, new_locations)
        filtered_locations = remove_unused_locations_tsp(locations, params["customers"], params["start_node"])

        tsp_result = run_request(
            current_time=params["start_time"],
            current_location=params["start_node"],
            customers=params["customers"],
            duration=durations,
            load=demands,
            do_loading_unloading=do_loading_unloading,
            cancelled_customers=cancel_customers,
            n_hyperparams=params_aco["n_hyperparams"],
        )
        result = tsp_result_2_output(
            start_time=params["start_time"],
            start_node=params["start_node"],
            duration=durations,
            load=demands,
            locations=new_locations,
            do_loading_unloading=do_loading_unloading,
            cancelled_customers=cancel_customers,
            tsp_result=tsp_result,
        )

        time_end = datetime.datetime.now()
        time_diff = (time_end - time_start).total_seconds()
        result["time_diff"] = time_diff

        # Save results
        if params["auth"]:
            duration = int(result["duration"])
            vehicles = [{"tours": [result["vehicle"]], "totalDuration": result["duration"]}]  # no capacity
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=filtered_locations,
                vehicles=vehicles,
                duration=duration,
                errors=errors,
            )

        if errors:
            result["errors"] = errors

        # Respond
        success(self, result)
