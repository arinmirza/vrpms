import json
from http.server import BaseHTTPRequestHandler
from api.database import DatabaseVRP
from api.helpers import fail, success, remove_unused_locations
from api.parameters import parse_common_vrp_parameters, parse_vrp_sa_parameters
from src.vrp.sa.simulated_annealing import solve


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hi, this is the VRP Simulated Annealing endpoint".encode("utf-8"))

    def do_POST(self):
        # Read
        content_length = int(self.headers.get("Content-Length", 0))
        content_string = str(self.rfile.read(content_length).decode("utf-8"))
        content = json.loads(content_string)

        # Parse parameters
        errors = []
        params = parse_common_vrp_parameters(content, errors)
        params_sa = parse_vrp_sa_parameters(content, errors)

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
        
        result = solve(
            durations=durations,
            locations=locations,
            customer_count=len(locations) - 1,
            vehicle_count=len(params["capacities"]),
            vehicle_capacity=params["capacities"][0],
            max_cycles=params_sa["max_cycles"],
            initial_temperature=params_sa['initial_temperature'],
            cooling_factor=params_sa["cooldown_factor"],
            step_length=params_sa["step_length"],
            terminate_after=params_sa["terminate_after"],
            repeat_annealing=5,
            ignored_customers=params["ignored_customers"])
        
        # Save results
        if params["auth"]:
            duration_max = int(result["durationMax"])
            duration_sum = int(result["durationSum"])
            database.save_solution(
                name=params["name"],
                description=params["description"],
                locations=remove_unused_locations(
                    locations, params["ignored_customers"], params["completed_customers"]
                ),
                vehicles=result["vehicles"],
                duration_max=duration_max,
                duration_sum=duration_sum,
                errors=errors,
            )

        if errors:
            result["errors"] = errors

        # Respond
        success(self, result)