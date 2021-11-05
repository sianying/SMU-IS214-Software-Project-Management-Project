from flask import Blueprint
routes = Blueprint('routes', __name__)

from .courses_routes import *
from .classes_routes import *
from .staff_routes import *
from .section_routes import *
from .quiz_routes import *
from .attempts_routes import *
from .request_routes import *
from .progress_routes import *