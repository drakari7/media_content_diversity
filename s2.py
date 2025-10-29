import base64
import io
import os
from flask import Flask, render_template, url_for, request
from matplotlib.figure import Figure

app = Flask(__name__)

graph_dir = "./static/graphs/"
os.makedirs(graph_dir, exist_ok=True)

@app.route("/", methods=["POST", "GET"])
def home():
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 1.5, 4])

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # return render_template('home.html')
    return f"<img src='data:image/png;base64,{data}'/>"


if __name__ == "__main__":
    app.run(debug=True)
