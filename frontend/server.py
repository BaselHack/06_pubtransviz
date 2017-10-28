from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')

@app.route("/helloworld")
def hello():
    return "Hello World!" 


@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)
