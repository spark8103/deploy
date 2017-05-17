# coding: utf-8
from flask import render_template, redirect, request, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from . import deploy
from .. import flash_errors
from .forms import AddDeployForm, JenkinsExecForm
from ..jenkins_ext import job_get_number, job_build, job_get_svn
from ..svn_ext import svn_tag_list
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
    if form.validate_on_submit():
        module = form.module.data
        version = form.version.data
        deploy_dir = request.form.getlist("deploy_dir[]")
        command = os.path.join(Config.BASE_DIR, 'scripts\\test.py')
        task_result = celery_runner.do_long_running_task.apply_async([command])
        result = {'r': 0, 'task_id': task_result.id}
    else:
        result = {'r': 1, 'error': form.errors}
    return jsonify(result)


@deploy.route('/deploy-module-output/<string:task_id>')
@login_required
def deploy_module_output(task_id):
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


@deploy.route('/deploy-module-status/<string:task_id>')
@login_required
def deploy_module_status(task_id):
    task = celery_runner.do_long_running_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        result = "Task not found"
        resp = make_response((result, 404))
        return resp
    if task.state == "PROGRESS":
        result_obj = {'Status': "PROGRESS",
                      'description': "Task is currently running",
                      'returncode': None}
    else:
        try:
            return_code = task.info['returncode']
            description = task.info['description']
            if return_code is 0:
                result_obj = {'Status': "SUCCESS",
                              'description': description}
            else:
                result_obj = {'Status': "FLANSIBLE_TASK_FAILURE",
                              'description': description,
                              'returncode': return_code}
        except:
            result_obj = {'Status': "CELERY_FAILURE"}

    return jsonify(result_obj)


@deploy.route('/deploy-module-history')
@login_required
def deploy_module_history():
    return render_template('deploy/deploy_history.html')


@deploy.route('/jenkins-building', methods=['GET', 'POST'])
@login_required
def jenkins_building():
    form = JenkinsExecForm()
    print form.data
    print form.validate_on_submit()
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


@deploy.route('/svn-tags')
@login_required
def svn_tags():
    job_name = request.args.get('job_name')
    if job_name:
        svn_url = job_get_svn(job_name)
        if svn_url['tag_dir']:
            svn_tag = svn_tag_list(svn_url['tag_dir'], job_name)
        else:
            svn_tag = {}
        return jsonify(svn_tag)
    else:
        return jsonify({})