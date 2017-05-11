# coding: utf-8
from flask import Flask, flash, current_app
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from celery import Celery
from config import config


bootstrap = Bootstrap()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'user.login'
login_manager.login_message = u"Please Login."
login_manager.login_message_category = "info"


def make_celery(app):
    celery = Celery(app.import_name, broker=current_app.config['CELERY_BROKER_URL'])
    celery.conf.update(current_app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# Initialize Celery
celery = make_celery( Flask(__name__))


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

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

#    from .deploy import deploy as project_blueprint
#    app.register_blueprint(project_blueprint, url_prefix='/deploy')

    return app
