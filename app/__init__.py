# coding: utf-8
from flask import Flask, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import config, Config
from celery import Celery


bootstrap = Bootstrap()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'user.login'
login_manager.login_message = u"Please Login."
login_manager.login_message_category = "info"


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)
    celery.conf.update(app.config)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .deploy import deploy as deploy_blueprint
    app.register_blueprint(deploy_blueprint, url_prefix='/deploy')

    from .ansible import ansible as ansible_blueprint
    app.register_blueprint(ansible_blueprint, url_prefix='/ansible')

    return app