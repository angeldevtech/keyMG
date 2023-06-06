from flask import jsonify, render_template, request
from .extensions import *
from .service.spotifyapi import *

def index():
    return render_template("index.html")

def discover():
    return render_template("discover.html")

def community():
    return render_template("community.html")

def about_us():
    return render_template("about_us.html")

def autocomplete():
    data = request.args.get('query')
    token = get_token()
    response = search_for_id_track(token=token,name_song=data)
    return jsonify(response)

def search():
    return 1