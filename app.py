from flask import Flask, render_template

from aws_manager.dask_setup import Brain

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/start')
def start():
    brain = Brain(security_group='VeryBadSecurity')
    url = brain.main()
    return render_template("start.html", url=url)
