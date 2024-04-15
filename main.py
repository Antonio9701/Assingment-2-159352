import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests

VALID_IDS = ['12345678', '87654321']
OMDB_API_KEY = '7deb6267'
DOG_API_URL = 'https://dog.ceo/api/breeds/image/random'
CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
DUCK_API_URL = 'https://random-d.uk/api/v2/random'
user_data = {}


def fetch_random_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if type(data) is list:
                return data[0]['url']
            else:
                return data['message']
    except Exception as e:
        print(f"Error fetching image from {url}: {str(e)}")
    return None


def fetch_movie_recommendation():
    query = "your_query"
    url = f'https://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'Search' in data:
                return data['Search'][0]['Title']
    except Exception as e:
        print(f"Error fetching movie from {url}: {str(e)}")
    return None


def perform_career_assessment(input_data):
    # collect the list of questions' answers
    question_data = [int(input_data['question[' + str(i + 1) + ']'][0]) for i in range(20)]

    # compute mean score
    mean_score = sum(question_data) // len(question_data)

    # categorize based on this mean_value
    if mean_score > 3:
        assessment = "You seem highly ambitious, consider aiming for a leadership role in your career."
    elif mean_score > 1:
        assessment = "You have a balanced personality, a collaborative role in projects might be suitable for you."
    else:
        assessment = "You seem interested in focused and detailed work, research or specialist roles may fit you."

    return assessment


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.authenticate():
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))
            return
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/style.css':
            self.serve_static_file('style.css')
        elif parsed_path.path == '/form':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('psycho.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path.startswith('/view/'):
            _, _, user = parsed_path.path.partition('/view/')
            user = user.split('/')[0]  # Make sure 'user' is only the username
            if user in user_data:
                if '/input' in parsed_path.path:
                    self.serve_json(user_data[user]['input'])
                elif '/profile' in parsed_path.path:
                    self.serve_json(user_data[user]['profile'])
                elif '/petImages' in parsed_path.path:
                    self.serve_json(user_data[user]['pet_images'])
                else:
                    self.send_error(404, "Unknown view")
            else:
                self.serve_json({"message": f"No data available for user {user}"})
        else:
            self.send_error(404)

    def do_POST(self):
        if not self.authenticate():
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))
            return
        if self.path == '/analysis':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)
            name = form_data.get('name', [''])[0]
            gender = form_data.get('gender', [''])[0]
            pets = form_data.get('pets', [])
            profile = {
                'name': name,
                'gender': gender,
                'career_assessment': perform_career_assessment(form_data),
                'movie_recommendation': fetch_movie_recommendation()
            }
            pet_images = {}
            for pet in pets:
                if pet == 'dog':
                    image_url = fetch_random_image(DOG_API_URL)
                elif pet == 'cat':
                    image_url = fetch_random_image(CAT_API_URL)
                elif pet == 'duck':
                    image_url = fetch_random_image(DUCK_API_URL)
                pet_images[pet] = image_url
            global user_data
            user_data[name] = {
                'input': form_data,
                'profile': profile,
                'pet_images': pet_images
            }
            response_data = {'message': 'Profile generated successfully'}
            print("User Data:", user_data)
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

    def serve_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def serve_static_file(self, path):
        try:
            with open(path, 'rb') as f:
                self.send_response(200)
                if path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                else:
                    self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404)


def run():
    host = 'localhost'
    port = 8000
    server_address = (host, port)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    print(f'Starting server on {host}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, shutting down the server')
        httpd.server_close()


if __name__ == '__main__':
    run()
