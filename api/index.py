import datetime
import json
from http.server import BaseHTTPRequestHandler

# Absolute import modules inside src folder
from src.vrp.ant_colony.aco_hybrid import run as vrp_aco
from src.vrp.brute_force.brute_force import run as vrp_bf
from src.tsp.ant_colony.aco_hybrid import run as tsp_aco
from src.tsp.brute_force.brute_force import run as tsp_bf
from src.tsp.simulated_annealing.simulated_annealing import run as tsp_sa

from urllib.parse import urlparse, parse_qs

SUPABASE_URL = "https://pkeygmzuwfucblldmkjn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZXlnbXp1d2Z1Y2JsbGRta2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTc5NzU0MTksImV4cCI6MjAxMzU1MTQxOX0.5TsK_pH0xsMyJWo_XPXt4NhsuS-vW6MAcj575WskZ8s"
SUPABASE_URL_KEY_FILE = "../data/supabase/supabase_url_key.txt"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        program_mode = query_params["program_mode"][0] if "program_mode" in query_params else "no_program_mode"
        if program_mode not in ["vrp", "tsp"]:
            program_mode = "no_program_mode"
        algorithm = query_params["algorithm"][0] if "algorithm" in query_params else "no_algorithm"
        if algorithm not in ["aco", "bf", "sa"]:
            algorithm = "no_algorithm"
        input_dict = {"program_mode": program_mode, "algorithm": algorithm}

        result = "no_result"
        time_start = datetime.datetime.now()
        if program_mode != "no_program_mode" and algorithm != "no_algorithm":
            if program_mode == "vrp" and algorithm == "aco":
                result = vrp_aco(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
            elif program_mode == "vrp" and algorithm == "bf":
                result = vrp_bf(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
            elif program_mode == "tsp" and algorithm == "aco":
                result = tsp_aco(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
            elif program_mode == "tsp" and algorithm == "bf":
                result = tsp_bf(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
            elif program_mode == "tsp" and algorithm == "sa":
                result = tsp_sa(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY, supabase_url_key_file=None)
        time_end = datetime.datetime.now()
        time_diff = (time_end - time_start).total_seconds()

        # Construct an example response
        body = {"input_dict": input_dict, "result": result, "time_diff": time_diff}

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        encoded_body = json.dumps(body).encode("utf-8")

        # Write response body into handler
        self.wfile.write(encoded_body)

        return

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Read post body length
        content_len = int(self.headers.get("Content-Length", 0))

        # Initialize empty json
        body = {}

        # Try to load json from body
        try:
            body = json.loads(str(self.rfile.read(content_len)))
        except:
            pass

        # Send the exact body back as response
        encoded_body = json.dumps(body).encode("utf-8")

        # Write response body into handler
        self.wfile.write(encoded_body)
