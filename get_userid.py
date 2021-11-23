from flask import Flask

app = Flask(__name__)

@app.route("/")
def index(arg1, arg2):
    print(f"This is arg1 {arg1}")
    print(f"This is arg2 {arg2}")
    return bytes("<p>Hello, this is a test</p>", "UTF-8")