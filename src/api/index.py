import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Construct an example dictionary 
        data = {
            'example-message': 'Hello from VRP microservice',
            'example-duration': '1 hour',
            'example-status': 'working'
        }

        # Convert the dictionary into JSON and serialize it, then encode as utf8
        body = json.dumps(data).encode('utf-8')

        # Write response body into handler
        self.wfile.write(body)
        
        return
