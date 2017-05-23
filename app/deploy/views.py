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
import os, json, urllib2, base64, time
from datetime import datetime


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
        deploy_dir = ','.join(request.form.getlist("deploy_dir[]"))
        exec_script = Config.DEPLOY_SCRIPT
        command = str.format("{0} -m {1} -d {2} -v {3}", exec_script, module, deploy_dir, version)
        print "ansible_command - " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " : " + command
        task_result = celery_runner.deploy_running_task.apply_async([command])
        result = {'r': 0, 'task_id': task_result.id, 'Location': url_for('.deploy_module_status', task_id=task_result.id)}
    else:
        result = {'r': 1, 'error': form.errors}
    return jsonify(result)


@deploy.route('/deploy-module-status/<string:task_id>')
@login_required
def deploy_module_status(task_id):
    task = celery_runner.deploy_running_task.AsyncResult(task_id)
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
                              'Out': task.info['output'].encode('utf-8').strip(),
                              'description': description,
                              'returncode': return_code}
            else:
                result_obj = {'Status': "FLANSIBLE_TASK_FAILURE",
                              'Out': task.info['output'].encode('utf-8').strip(),
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
    if form.validate_on_submit():
        job = form.job.data
        tag = form.tag.data
        result = job_build(job_name=job, tag=tag)
        re = {'result': result['result'], 'build_number': result['number'], 'revisions': result['changeSet']['revisions']}
        return jsonify(re)
    else:
        return render_template('deploy/ansible_command.html', form=form)


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
            svn_tag = svn_tag_list(url=svn_url['tag_dir'], tags_filter=svn_url['tags_filter'])
        else:
            svn_tag = {}
        return jsonify(svn_tag)
    else:
        return jsonify({})


@deploy.route('/flower-list')
@login_required
def flower_list():
    task_id = request.args.get('task_id')
    if task_id:
        tasks_api = Config.FLOWER_URL + 'api/task/info/' + task_id
        request_url = urllib2.Request(tasks_api)
        base64string = base64.encodestring('%s:%s' % (Config.FLOWER_USER, Config.FLOWER_PASSWORD)).replace('\n', '')
        request_url.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request_url)
        data = str(response.read().decode('utf-8')).replace('\'', '"')
        results = json.loads(data)
        if results['name'] != 'app.celery_runner.deploy_running_task':
            results = {}
    else:
        tasks_api = Config.FLOWER_URL + 'api/tasks'
        request_url = urllib2.Request(tasks_api)
        base64string = base64.encodestring('%s:%s' % (Config.FLOWER_USER, Config.FLOWER_PASSWORD)).replace('\n', '')
        request_url.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request_url)
        data = response.read().decode('utf-8')
        values = json.loads(data)
        results = []
        for key, value in values.iteritems():
            if value['name'] != 'app.celery_runner.deploy_running_task':
                continue
            uuid = value['uuid']
            args = value['args'][3:-2]
            if value['result']:
                result = json.loads(str(value['result']).replace('\"', '^').replace('\'', '"').
                                    replace('\\x1b', '').replace('\\n', '<br />'))
            else:
                result = ''
            timestamp = datetime.fromtimestamp(value['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            state = value['state']
            results.append({
                'uuid': uuid,
                'args': args,
                'name': args.split()[2],
                'deploy_dir': args.split()[4],
                'build_number': args.split()[6],
                'result': result,
                'timestamp': timestamp,
                'state': state
            })
        # results = [{'args': value['args'][3:-2], 'result': json.loads(str(value['result']).replace('\'', '"')),
        #            'timestamp': datetime.fromtimestamp(value['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
        #            'state': value['state'], 'uuid': value['uuid']}
        #           for key, value in values.iteritems() if value['name'] == 'app.celery_runner.deploy_running_task']
    return jsonify(results)