from flask import Flask

app = Flask(__name__)

@app.route("/")
def index(arg1, arg2):
    return "<p>Hello World<p>"