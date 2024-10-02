# Orchestrator server

from flask import Flask


app = Flask(__name__)
@app.route("/")
def helloworld():
    return "WiGreen 2K24!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6060)
