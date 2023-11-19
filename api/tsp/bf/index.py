import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseTSP
from api.helpers import fail, success
from api.parameters import parse_common_tsp_parameters
from src.tsp.brute_force.brute_force import run_request
from src.utilities.helper.data_helper import convert_locations
from src.utilities.helper.result_2_output import tsp_result_2_output


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the TSP Brute Force endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_tsp_parameters(content, errors)

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

        locations = convert_locations(locations)
        bf_result = run_request(
            current_time=params["start_time"],
            current_location=params["start_node"],
            customers=params["customers"],
            duration=durations,
        )
        result = tsp_result_2_output(
            start_time=params["start_time"],
            start_node=params["start_node"],
            duration=durations,
            locations=locations,
            bf_result=bf_result
        )

        # Save results
        if params["auth"]:
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=locations,
                vehicle=result["vehicle"],
                duration=result["duration"],
                errors=errors,
            )

        if len(errors) > 0:
            fail(self, errors)
            return

        # Respond
        success(self, result)
