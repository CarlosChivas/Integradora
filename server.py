# Server
from flask import Flask, render_template, request, jsonify
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import json

app = Flask(__name__, static_url_path='')

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


data = {
    'cars': [], 
    'trafficLights': []
}

@app.route('/')
def string():
    return json.dumps(data)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write(bytes(string(), 'utf-8'))

    @app.route('/', methods = ['POST'])
    def do_POST():
        global data
        if request.method == 'POST':
            post_data = request.data
            post_data_json = json.loads(post_data)
            data = post_data_json
        return ""

@app.route('/delete')
def delete():
    global data
    data = {
        'cars': [], 
        'trafficLights': []
    }
    return data



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
