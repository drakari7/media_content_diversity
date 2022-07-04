import os
from flask import Flask, render_template, url_for, request
from multiprocessing import Process

from sparklines import make_graph, compare_graphs

app = Flask(__name__)

graph_dir = "./static/graphs/"
os.makedirs(graph_dir, exist_ok=True)

@app.route("/", methods=["POST", "GET"])
def home():
    # If we get a query in site
    if request.method == "POST":
        q1 = request.form["q1"].title()
        q2 = request.form["q2"].title()

        if q2:          # If second argument is not null
            src = graph_dir + 'metadata/' + q1 + '_' + q2 + '.jpg'

            # If doesn't already exist, plot graph in another process
            if not os.path.isfile(src):
                p = Process(target=compare_graphs, args=[q1, q2])
                p.start()
                p.join()

            return render_template("home.html", q1=q1, q2=q2, path=src)

        else:           # if only 1 argument
            src = graph_dir + 'metadata/' + q1 + '.jpg'

            # If doesn't already exist, plot graph in another process
            if not os.path.isfile(src):
                p = Process(target=make_graph, args=[q1])
                p.start()
                p.join()

            return render_template("home.html", q1=q1, path=src)

    # Else just serve default homepage
    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
