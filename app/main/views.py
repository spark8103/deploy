# coding: utf-8
from flask import render_template, abort, current_app, request
from flask_login import login_required, current_user
from . import main


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
@login_required
def index():
    print current_user.username
    return render_template('index.html')