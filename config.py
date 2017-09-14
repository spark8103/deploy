# coding: utf-8
import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rxdXHXmrQurSKxsh35'
    USER_LIST = {'admin': {'password': 'admin123'}}
    SITE_NAME = "deploy"
    BASE_DIR = basedir
    BOOTSTRAP_SERVE_LOCAL = True

    # Deploy configuration
    DEPLOY_SCRIPT = 'd://spark//git//deploy//scripts//test.py'
    DEPLOY_INVENTORY_FILE = '/opt/soft_build/DEPLOY/inventory_dir/project'

    # Flower configuration
    FLOWER_URL = 'http://127.0.0.1:5555/'
    FLOWER_USER = 'admin'
    FLOWER_PASSWORD = 'admin123'

    # Celery configuration
    CELERY_BROKER_URL = 'redis://172.31.217.201:6379/0'
    CELERY_RESULT_BACKEND = 'redis://172.31.217.201:6379/0'
    CELERY_TASK_SERIALIZER = 'msgpack'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
    CELERY_ENABLE_UTC = True
    CELERYD_LOG_FILE = "logs/celery.log"

    CELERYBEAT_SCHEDULE = {
        'update_inventory_prod-600-seconds': {
            'task': 'celery_tasks.cmd',
            'args': ['/opt/app/applications/bd-deploy/scripts/update_inventory_prod.py'],
            'schedule': timedelta(seconds=600)
        },
    }

    # Jenkins configuration
    JENKINS_URL = 'http://172.31.217.62:8080/'
    JENKINS_USER = 'zhangchuanshuang'
    JENKINS_TOKEN = '017f91b93c065934218aed003e1475fe'

    # SVN configuration
    SVN_URL = 'http://10.205.59.16/svn/'
    SVN_USER = "apprun"
    SVN_PASSWORD = "apprun"

    # GITLAB configuration
    GITLAB_SERVER = 'http://gitlab.ttttttt.com'
    GITLAB_TOKEN = 'tokkkkkk-BPXg'

    # ansible configuration
    ANSIBLE_INVENTORY_FILE = 'd://spark//git//deploy//scripts//inventory_prod'
    ANSIBLE_TEMP_INVENTORY_FILE = 'd://spark//git//deploy//scripts//inventory_temp'
    ANSIBLE_COMMAND = 'ansible'
    ANSIBLE_USER = 'apprun'
    ANSIBLE_KEY = 'd://spark//git//deploy//ssh_keys//id-rsa'
    ANSIBLE_PATH = 'd://spark//git//deploy//ansible//'


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