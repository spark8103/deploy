# deploy

------

## Init
### Install requirements
pip install -r requirements/requirements.txt

### start celer_work
```shell
celery worker -A celery_worker.celery -l INFO
```

## Run Server
```shell
python manage.py runserver --threaded
```