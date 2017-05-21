# coding: utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rxdXHXmrQurSKxsh35'
    USER_LIST = {'admin': {'password': 'admin123'}}
    SITE_NAME = "deploy"
    BASE_DIR = basedir
    BOOTSTRAP_SERVE_LOCAL = True
    DEPLOY_SCRIPT = 'd://spark//git//deploy//scripts//test.py'
    FLOWER_URL = 'http://127.0.0.1:5555/'
    FLOWER_USER = 'admin'
    FLOWER_PASSWORD = 'admin123'

    # Celery configuration
    CELERY_BROKER_URL = 'redis://172.31.217.201:6379/0'
    CELERY_RESULT_BACKEND = 'redis://172.31.217.201:6379/0'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    CELERYD_LOG_FILE = "logs/celery.log"

    # Jenkins configuration
    JENKINS_URL = 'http://172.31.217.62:8080/'
    JENKINS_USER = 'zhangchuanshuang'
    JENKINS_TOKEN = '017f91b93c065934218aed003e1475fe'

    # SVN configuration
    SVN_URL = 'http://10.205.59.16/svn/'
    SVN_USER = "apprun"
    SVN_PASSWORD = "apprun"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}