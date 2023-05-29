from flask import jsonify, render_template
from .extensions import *


def index():
    return render_template("index.html")


def search():
    return render_template("search.html")
