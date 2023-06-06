from flask import jsonify, render_template
from .extensions import *

def index():
    return render_template("index.html")

def discover():
    return render_template("discover.html")

def community():
    return render_template("community.html")

def about_us():
    return render_template("about_us.html")