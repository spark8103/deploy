# coding: utf-8
from flask import render_template, redirect, request, url_for, flash, \
    jsonify
from flask_login import login_required, current_user
from . import deploy
from .. import flash_errors
from .forms import AddDeployForm
from .. import celery
import random, time
from ..jenkins_ext import jobs_list_get, job_build

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@deploy.route('/deploy')
@login_required
def deploy_main():
    add_deploy_form = AddDeployForm()
    return render_template('deploy/deploy.html', add_deploy_form=add_deploy_form)


@deploy.route('/deploy-list')
@login_required
def deploy_list():
    if request.args.get('module'):
        deploys = {"sss:" "aa"}
    else:
        deploys = {"sss:" "aa"}
    if not deploys:
        return jsonify({})
    else:
        # Serialize the queryset
        result = deploys
        return jsonify(result)


@deploy.route('/deploy-add', methods=['POST'])
@login_required
def deploy_add():
    form = AddDeployForm(data=request.get_json())
    if form.validate_on_submit():
        flash('deploy: ' + form.module.data + 'is success.')
    else:
        flash_errors(form)
    return redirect(url_for('.deploy_main'))


@deploy.route('/deploy-history')
@login_required
def deploy_history():
    return render_template('deploy/deploy_history.html')


@deploy.route('/longtask', methods=['POST'])
@login_required
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('.taskstatus', task_id=task.id)}


@deploy.route('/status/<task_id>')
@login_required
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)