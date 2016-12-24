from flask import Blueprint

term_bp = Blueprint('term_bp', __name__)

from . import views