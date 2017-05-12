# coding: utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SITE_NAME = "deploy"
    BOOTSTRAP_SERVE_LOCAL = True

    # Celery configuration
    CELERY_BROKER_URL = 'redis://172.31.217.201:6379/0'
    CELERY_RESULT_BACKEND = 'redis://172.31.217.201:6379/0'
    CELERY_TASK_SERIALIZER = 'json'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}