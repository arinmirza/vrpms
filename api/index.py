import json
from http.server import BaseHTTPRequestHandler

# Absolute import modules inside src folder
from src.vrp.ant_colony.aco_hybrid import run


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Construct an example response
        body = {
            "aco": run(n=16),
        }

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
