from flask import Flask, Response
import os

app = Flask(__name__)

COUNTER_FILE = "content.txt"

def get_count():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
        return 0
    with open(COUNTER_FILE, "r") as f:
        return int(open(COUNTER_FILE).read().strip())

def increment_count():
    count = get_count() + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
    return count

@app.route("/hi.svg")
def serve_svg():
    increment_count()
    svg = """
    <svg width="100" height="30" xmlns="http://www.w3.org/2000/svg">
      <text x="10" y="20" font-family="Arial" font-size="20" fill="black">Hi</text>
    </svg>
    """
    return Response(svg, mimetype="image/svg+xml")

@app.route("/count")
def show_count():
    return Response(str(get_count()), mimetype="text/plain")

@app.route("/")
def home():
    return "Welcome to the SVG Counter App! Visit /hi.svg or /count."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
