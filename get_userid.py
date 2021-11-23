from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    print(f"This is arg1 {arg1}")
    print(f"This is arg2 {arg2}")
    return render_template("index.html")


if __name__ == "__main__":
    app.run()