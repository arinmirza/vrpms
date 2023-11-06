import datetime
import json
from http.server import BaseHTTPRequestHandler

# Absolute import modules inside src folder
from src.vrp.ant_colony.aco_hybrid import run
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        program_mode = query_params["program_mode"][0] if "program_mode" in query_params else "default"
        algorithm = query_params["algorithm"][0] if "algorithm" in query_params else "default"
        data_dict = {"program_mode": program_mode, "algorithm": algorithm}

        supabase_url_key_file = "../data/supabase/supabase_url_key.txt"

        time_start = datetime.datetime.now()
        aco_result = run(supabase_url_key_file=supabase_url_key_file)
        time_end = datetime.datetime.now()
        time_diff = time_end - time_start
        time_diff = time_diff.total_seconds()

        # Construct an example response
        body = {"aco": aco_result, "time_diff": time_diff, "data_dict": data_dict}

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
