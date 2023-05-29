from flask import Blueprint
from . import controllers

index_blueprint = Blueprint("index", "index", url_prefix="/")
index_blueprint.add_url_rule("", "", controllers.index)

search_blueprint = Blueprint("search", "search", url_prefix="/search")
search_blueprint.add_url_rule("", "", controllers.search)
