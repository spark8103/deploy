# coding: utf-8
from flask import render_template, redirect, request, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from . import deploy
from .. import flash_errors
from .forms import AddDeployForm, JenkinsExecForm
from ..jenkins_ext import job_get_number, job_build
from config import Config
from .. import celery_runner
import os


@deploy.route('/deploy-module')
@login_required
def deploy_module():
    add_deploy_form = AddDeployForm()
    return render_template('deploy/deploy_module.html', add_deploy_form=add_deploy_form)


@deploy.route('/deploy-module-add', methods=['POST'])
@login_required
def deploy_module_add():
    form = AddDeployForm(data=request.get_json())
    print Config.BASE_DIR
    print form.data
    command = os.path.join(Config.BASE_DIR, 'scripts\\test.py')
    print command
    task_result = celery_runner.do_long_running_task.apply_async([command])
    print task_result
    result = {'task_id': task_result.id}
    if form.validate_on_submit():
        flash('deploy: ' + form.module.data + 'is success.')
    else:
        flash_errors(form)
    return jsonify(result)


@deploy.route('/deploy-module-status/<string:task_id>')
@login_required
def deploy_module_status(task_id):
    task = celery_runner.do_long_running_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        result = "Task not found"
        resp = make_response((result, 404))
        return resp
    if task.state == "PROGRESS":
        result = task.info['output']
    else:
        result = task.info['output']
    # result_out = task.info.replace('\n', "<br>")
    # result = result.replace('\n', '<br>')
    # return result, 200, {'Content-Type': 'text/html; charset=utf-8'}
    resp = make_response((result, 200))
    resp.headers['content-type'] = 'text/plain'
    return resp


@deploy.route('/deploy-module-history')
@login_required
def deploy_module_history():
    return render_template('deploy/deploy_history.html')


@deploy.route('/jenkins-building', methods=['GET', 'POST'])
@login_required
def jenkins_building():
    form = JenkinsExecForm()
    if form.validate_on_submit():
        job = form.job.data
        result = job_build(job)
        re = {'result': result['result'], 'build_number': result['number'], 'revisions': result['changeSet']['revisions']}
        return jsonify(re)
    else:
        return render_template('deploy/jenkins_building.html', form=form)


@deploy.route('/jenkins-job-number')
@login_required
def jenkins_job_number():
    job_name = request.args.get('job_name')
    if job_name:
        return jsonify(job_get_number(job_name))
    else:
        return jsonify({})