# coding: utf-8
from flask import Blueprint

wiki = Blueprint('wiki', __name__)

from . import views