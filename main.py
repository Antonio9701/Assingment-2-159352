import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Sample valid student IDs (for demonstration)
VALID_IDS = ['12345678', '87654321']


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check for authentication before serving any content
        if not self.authenticate():
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))
            return

        # Parse the requested URL
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Define routes
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/form':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('psycho.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/style.css':  # Serve style.css
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('style.css', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/view/input':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {'message': 'Received input data'}
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif parsed_path.path == '/view/profile':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            profile_data = {'profile': 'Generated psychological profile'}
            self.wfile.write(json.dumps(profile_data).encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        # Check for authentication before handling the form submission
        if not self.authenticate():
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))
            return

        # Handle POST requests (form submissions)
        if self.path == '/analysis':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)

            # Extract form data
            name = form_data.get('name', [''])[0]
            gender = form_data.get('gender', [''])[0]
            # Extract and process other form fields

            # Dummy response for demonstration
            response_data = {'name': name, 'gender': gender, 'message': 'Form submitted successfully'}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404)

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def authenticate(self):
        if 'Authorization' in self.headers:
            auth_header = self.headers['Authorization']
            credentials = auth_header.split(' ')[1]
            username, password = base64.b64decode(credentials).decode('utf-8').split(':')
            if username in VALID_IDS and username == password:
                return True
        return False


def run():
    # Server settings
    host = 'localhost'
    port = 8000
    server_address = (host, port)

    # Start HTTP server
    httpd = HTTPServer(server_address, MyHTTPHandler)
    print(f'Starting server on {host}:{port}')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping server')
        httpd.server_close()


if __name__ == '__main__':
    run()

