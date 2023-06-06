from flask import Blueprint
from .controllers import index,discover,community,about_us

index_blueprint = Blueprint("index", "index", url_prefix="/")
index_blueprint.add_url_rule("", "", index)

discover_blueprint = Blueprint("discover", "discover", url_prefix="/discover")
discover_blueprint.add_url_rule("", "", discover)

community_blueprint = Blueprint("community", "community", url_prefix="/community")
community_blueprint.add_url_rule("", "", community)

about_us_blueprint = Blueprint("about_us", "about_us", url_prefix="/about-us")
about_us_blueprint.add_url_rule("", "", about_us)