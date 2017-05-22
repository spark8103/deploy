# coding: utf-8
from flask import Blueprint

ansible = Blueprint('ansible', __name__)

from . import views
