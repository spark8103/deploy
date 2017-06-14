# coding: utf-8
from flask import Blueprint

ansibleplaybook = Blueprint('ansibleplaybook', __name__)

from . import views
