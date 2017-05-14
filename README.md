# deploy

------

## Init
### Install requirements
pip install -r requirements/requirements.txt

### start celer_work
```shell
celery worker -A celery_worker.celery -P gevent -c 10 -l INFO
```

## Run Server
```shell
python manage.py runserver --threaded
```

## reference
 * [celery-and-the-flask-application-factory-pattern](https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern)
 * [flansible](https://github.com/trondhindenes/flansible.git)