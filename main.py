import json
import os
import socket
import _thread
import sys
from typing import List, Dict, Optional, Any

import requests

http_separator = '\r\n'


class HTTPrequest:

    def __init__(self, cmd, path, headers, payload):
        self.cmd = cmd
        self.path = path
        self.headers = headers
        self.payload = payload


def parse_http_request(request):
    # Parses the http_request inorder to use later
    headers = request.decode().split('\r\n')
    reqline = headers.pop(0)
    payload = headers.pop()
    headers_dict = {}

    for header in headers:
        if header != '':
            k, v = header.split(': ')
            headers_dict[k] = v
    try:
        cmd, path, prot = reqline.split()
    except ValueError:
        cmd = ''
        path = ''
        payload = ''

    return HTTPrequest(cmd, path, headers_dict, payload)


def http_status(connection, status):
    connection.send(('HTTP/1.1 ' + status + http_separator).encode())


def deliver_200(connection):
    http_status(connection, '200 OK')


def deliver_404(connection):
    http_status(connection, '404 Not found')


def http_header(connection, headerline):
    connection.send((headerline + http_separator).encode())


def http_body(connection, payload):
    connection.send(http_separator.encode())
    connection.send(payload)


def read_file(filename, binary=False):
    if binary:
        mode = 'rb'
    else:
        mode = 'r'
    with open(filename, mode) as fin:
        content = fin.read()
    return content


def deliver_html(connection, filename):
    deliver_200(connection)
    content = read_file(filename)
    http_header(connection, 'Content-Type: text/html')
    http_body(connection, content.encode())


def deliver_gif(connection, filename):
    # Deliver content of GIF image file
    content = read_file(filename, binary=True)
    deliver_200(connection)
    http_header(connection, 'Content-Type: image/gif')
    http_header(connection, 'Accept-Ranges: bytes')
    http_body(connection, content)


def deliver_jpg(connection, filename):
    deliver_200(connection)
    content = read_file(filename, binary=True)
    http_header(connection, 'Content-Type: image/jpg')
    http_header(connection, 'Accept-Ranges: bytes')
    http_body(connection, content)


def deliver_json_string(connection, jsons):
    deliver_200(connection)
    http_header(connection, 'Content-Type: application/json')
    http_body(connection, jsons.encode())


def deliver_json(connection, filename):
    content = read_file(filename)
    deliver_json_string(connection, content)


def load_data(filename: str) -> Dict[str, Any]:
    with open(filename) as f:
        return json.load(f)


def parse_form_data(request):
    # Split the request into headers and body
    headers, body = request.decode().split(http_separator + http_separator, 1)

    # Parse the form data
    parsed_form_data = {}
    form_data_pairs = body.split('&')
    for pair in form_data_pairs:
        question, answer = pair.split('=')
        if question.startswith("question"):
            # Extract the question number and value from the question parameter
            question_number = (question.split("%5B")[1].split("%5D")[0])
            parsed_form_data[question_number] = int(answer)
        elif question.startswith(("message", "residence", "birthplace", "name")):
            parsed_form_data[question] = answer.replace('+', ' ')
        elif question.startswith("pets"):
            # Append the pet value to the pets array in parsed_form_data
            if "pets" not in parsed_form_data:
                parsed_form_data["pets"] = []
            parsed_form_data["pets"].append(answer)
        else:
            parsed_form_data[question] = answer


def extract_responses(data: Dict[str, Any]) -> Dict[str, int]:
    return {k: v for k, v in data.items() if isinstance(v, int)}


def calculate_job_scores(responses: Dict[str, int], job_scores: Dict[str, List[int]]) -> Dict[str, int]:
    job_scores_total = {}
    for job, scores in job_scores.items():
        total = sum(responses.get(str(i), 0) * score for i, score in enumerate(scores, 1))
        job_scores_total[job] = total
    return job_scores_total


def determine_best_job(job_scores_total: Dict[str, int]) -> str:
    return max(job_scores_total, key=job_scores_total.get)


def calculate_suitability(desired_job: str, job_scores_total: Dict[str, int]) -> int:
    return sum(1 for total in job_scores_total.values() if total > job_scores_total[desired_job])


def load_job_scores() -> Dict[str, List[int]]:
    return {
        "ceo": [1, 2, 4, 1, 1, 4, 1, 2, 4, 1, 3, 1, 3, 2, 4, 3, 4, 4, 1, 1],
        "astronaut": [1, 3, 2, 2, 1, 3, 3, 2, 1, 4, 1, 2, 4, 3, 2, 4, 2, 2, 4, 3],
        "doctor": [2, 3, 3, 3, 1, 3, 2, 3, 2, 4, 1, 2, 3, 3, 2, 3, 2, 2, 4, 3],
        "model": [2, 1, 2, 1, 2, 2, 3, 2, 1, 1, 3, 2, 3, 3, 4, 2, 4, 3, 1, 1],
        "rockstar": [3, 2, 3, 2, 2, 2, 3, 2, 2, 2, 1, 2, 2, 2, 3, 2, 3, 2, 2, 2],
        "refuse": [1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 4, 3, 3, 4, 1, 3, 3, 1, 3, 3]
    }


def fetch_data(uri: str) -> Optional[Dict[str, Any]]:
    response = requests.get(uri)
    if response.ok:
        return response.json()
    return None


def fetch_movie_data(desired_job: str, apis: Dict[str, str]) -> Optional[Dict[str, Any]]:
    movie_uri = apis.get(desired_job)
    if movie_uri:
        return fetch_data(movie_uri)
    return None


def download_image(uri: str) -> Optional[str]:
    response = requests.get(uri)
    if response.ok:
        filename = os.path.basename(uri)
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    return None


def download_pet_images(pets: List[str], apis: Dict[str, str]) -> List[Dict[str, str]]:
    pet_images = []
    for pet in pets:
        uri = apis.get(pet)
        if uri:
            image_data = fetch_data(uri)
            if image_data:
                if pet == 'dog':
                    image_uri = image_data.get('message')
                elif pet == 'cat':
                    image_uri = image_data[0].get('url')
                else:
                    image_uri = image_data.get('url')
                if image_uri:
                    filename = download_image(image_uri)
                    if filename:
                        pet_images.append({"name": pet, "image": filename})
    return pet_images


def analyze(data_filename: str, profile_filename: str):
    data = load_data(data_filename)
    responses = extract_responses(data)
    job_scores = load_job_scores()
    desired_job = data.get('job')
    apis = {
        "dog": "https://dog.ceo/api/breeds/image/random",
        "cat": "https://api.thecatapi.com/v1/images/search",
        "duck": "https://random-d.uk/api/v2/random",
        "ceo": "https://www.omdbapi.com/?apikey=ab374535&t=the+founder",
        "astronaut": "https://www.omdbapi.com/?apikey=ab374535&t=the+martian",
        "doctor": "https://www.omdbapi.com/?apikey=ab374535&t=patch+adams",
        "model": "https://www.omdbapi.com/?apikey=ab374535&t=zoolander",
        "rockstar": "https://www.omdbapi.com/?apikey=ab374535&t=YESTERDAY",
        "refuse": "https://www.omdbapi.com/?apikey=ab374535&t=MEN+AT+WORK"
    }

    job_scores_total = calculate_job_scores(responses, job_scores)
    best_job = determine_best_job(job_scores_total)
    suitability = calculate_suitability(desired_job, job_scores_total)
    movie_data = fetch_movie_data(desired_job, apis)
    pet_images = download_pet_images(data.get("pets", []), apis)

    profile = {
        'desired_job': desired_job,
        'best_suited_job': best_job,
        'suitability_for_chosen_job': suitability,
        'movie': movie_data,
        'pets': pet_images
    }

    with open(profile_filename, "w") as file:
        json.dump(profile, file)


def parse_authentication(request):
    headers = request.decode().split('\r\n')
    for header in headers:
        if header.startswith('Authorization:'):
            return header.split(' ')[-1]


def authenticate(connection, request):
    key = parse_authentication(request)
    correct_key = 'MjEwMDA4MDI6MjEwMDA4MDI='
    if key == correct_key:
        return True
    else:
        connection.send(b'HTTP/1.1 401 Unauthorized\r\n')
        # Request to authenticate
        connection.send(b'WWW-Authenticate: Basic realm="Web 159352"')
        connection.send(b'\r\n')
        return False


# request handler
def do_request(connectionSocket):
    # Extract just the HTTP command (method) and path from the request
    request = connectionSocket.recv(20240)
    http_request = parse_http_request(request)
    cmd, path = http_request.cmd, http_request.path

    if cmd == 'GET':
        sign_in_status = authenticate(connectionSocket, request)
        if sign_in_status:
            if path == '/':
                deliver_html(connectionSocket, 'index.html')
            elif path == '/form':
                deliver_html(connectionSocket, 'psycho.html')
            elif path == '/view/input':
                deliver_json(connectionSocket, 'input.json')
            elif path == '/view/profile':
                deliver_json(connectionSocket, 'profile.json')
            elif path == '/input.json':
                deliver_json(connectionSocket, path.strip('/'))
            elif path == '/profile.json':
                deliver_json(connectionSocket, path.strip('/'))
            elif path.endswith('.jpg'):
                deliver_jpg(connectionSocket, path.strip('/'))
            else:
                deliver_404(connectionSocket)
    elif cmd == 'POST':
        sign_in_status = authenticate(connectionSocket, request)
        if sign_in_status:
            if path == '/analysis':
                parse_form_data(request)
                analyze('input.json', 'profile.json')
                deliver_200(connectionSocket)
            else:
                deliver_404(connectionSocket)

    # Close the connection
    connectionSocket.close()


def main(serverPort):
    # Create the server socket object
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the server socket to the port
    mySocket.bind(('', serverPort))

    # Start listening for new connections
    mySocket.listen()

    while True:
        # Accept a connection from a client
        connectionSocket, addr = mySocket.accept()

        # Handle each connection in a separate thread
        _thread.start_new_thread(do_request, (connectionSocket,))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        serverPort = int(sys.argv[1])
    else:
        serverPort = 8080

    main(serverPort)
