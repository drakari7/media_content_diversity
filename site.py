import os
from flask import Flask, render_template, url_for, request
from multiprocessing import Process

from sparklines import make_graph

app = Flask(__name__)

graph_dir = "./static/graphs/"

@app.route("/", methods=["POST", "GET"])
def home():
    # If we get a query in site
    if request.method == "POST":
        query = request.form["query"]

        os.makedirs(graph_dir, exist_ok=True)
        src = graph_dir + 'metadata/' + query + '.jpg'

        # If doesn't already exist, plot graph in another process
        if not os.path.isfile(src):
            p = Process(target=make_graph, args=[query])
            p.start()
            p.join()

        return render_template("home.html", query=query, path=src)

    # Else just serve default homepage
    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
