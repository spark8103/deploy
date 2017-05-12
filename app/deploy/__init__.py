# coding: utf-8
from flask import Blueprint

deploy = Blueprint('deploy', __name__)

from . import views
