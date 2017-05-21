# deploy

------

## Init
### Install requirements
```shell
pip install -r requirements/requirements.txt
```

Install svn command.

## Development Run
### start celery_work
```shell
/opt/app/applications/bd-deploy/venv/bin/celery worker -A celery_worker.celery -P gevent -c 10 -l INFO
```

### start flower
```shell
/opt/app/applications/bd-deploy/venv/bin/flower -A celery_worker.celery --basic_auth=admin:admin123,admin2:admin321 --address=0.0.0.0 --port=5555
```

### Run Server
```shell
/opt/app/applications/bd-deploy/venv/bin/python manage.py runserver -h 0.0.0.0 -p 5000 --debug --reload --threaded
```

## Production Run
```shell
chown -R apprun:apprun /opt/app/applications/bd-deploy/
/opt/app/applications/bd-deploy/venv/bin/supervisord -c /opt/app/applications/bd-deploy/supervisord.conf
```

## Test script
```shell
/opt/app/applications/bd-deploy/scripts/deploy_test.sh -d lib,apps,config -m test-cmdb5 -v 9
```

## reference
 * [celery-and-the-flask-application-factory-pattern](https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern)
 * [flansible](https://github.com/trondhindenes/flansible.git)