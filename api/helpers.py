import json
from http.server import BaseHTTPRequestHandler


def get_parameter(name: str, content: dict, errors, optional=False):
    if name not in content and not optional:
        errors += [{ 'what': 'Missing parameter', 'reason': f"'{name}' was not provided" }]
    return content.get(name)


def remove_unused_locations(locations, ignored_customers, completed_customers):
    disregard = ignored_customers + completed_customers
    return [loc for loc in locations if loc['id'] not in disregard]
    

def fail(handler: BaseHTTPRequestHandler, errors):
    handler.send_response(400)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    response = { 'success': False, 'errors': errors }
    handler.wfile.write(json.dumps(response).encode('utf-8'))


def success(handler: BaseHTTPRequestHandler, result: dict):
    handler.send_response(200)
    handler.send_header('Content-type', 'application/json')
    handler.end_headers()
    response = { 'success': True, 'message': result }
    handler.wfile.write(json.dumps(response).encode('utf-8'))
