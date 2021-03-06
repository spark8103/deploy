# coding: utf-8
from flask import render_template, redirect, request, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from . import ansibleplaybook
from .forms import AddAnsiblePlaybookForm, AddOsInitForm, AddAnsiblePlaybookTempForm
from .. import flash_errors
from config import Config
from .. import celery_runner
import os, json, urllib2, base64, time, re
from ..ansible_ext import get_ansible_inventory_hosts, update_inventory_temp, get_ansible_playbook_vars
from datetime import datetime


@ansibleplaybook.route('/ansible-playbook')
@login_required
def ansible_playbook():
    add_deploy_form = AddAnsiblePlaybookForm()
    return render_template('ansible_playbook/ansible_playbook.html', add_deploy_form=add_deploy_form)


@ansibleplaybook.route('/ansible-playbook-add', methods=['POST'])
@login_required
def ansible_playbook_add():
    form = AddAnsiblePlaybookForm(data=request.get_json())
    if form.validate_on_submit():
        group = form.group.data
        host = form.host.data
        playbook = os.path.join(Config.ANSIBLE_PATH, form.playbook.data)
        extra_var = form.extra_var.data
        if host == "all":
            exec_command = str.format("{0} -i {1} --private-key={2} -e {3} {4} -l {5}", "ansible-playbook",
                                      Config.ANSIBLE_INVENTORY_FILE, Config.ANSIBLE_KEY, extra_var, playbook, group)
        else:
            exec_command = str.format("{0} -i {1} --private-key={2} -e {3} {4} -l {5}", "ansible-playbook",
                                      Config.ANSIBLE_INVENTORY_FILE, Config.ANSIBLE_KEY, extra_var, playbook, host)
        print "ansible_playbook - " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " : " + exec_command
        task_result = celery_runner.ansible_playbook_task.apply_async([exec_command])
        result = {'r': 0, 'task_id': task_result.id, 'Location': url_for('.ansible_playbook_status', task_id=task_result.id)}
    else:
        result = {'r': 1, 'error': form.errors}
    return jsonify(result)


@ansibleplaybook.route('/ansible-playbook-status/<string:task_id>')
@login_required
def ansible_playbook_status(task_id):
    task = celery_runner.ansible_playbook_task.AsyncResult(task_id)
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


@ansibleplaybook.route('/ansible-playbook-history')
@login_required
def ansible_playbook_history():
    return render_template('ansible_playbook/ansible_playbook_history.html')


@ansibleplaybook.route('/get-hosts')
@login_required
def get_hosts():
    group = request.args.get('group')
    if group:
        hosts = get_ansible_inventory_hosts(group)
        return jsonify(hosts)
    else:
        return jsonify({})


@ansibleplaybook.route('/flower-list')
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
        if results['name'] != 'app.celery_runner.ansible_playbook_task':
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
            if value['name'] != 'app.celery_runner.ansible_playbook_task':
                continue
            uuid = value['uuid']
            args = value['args'][3:-2]
            if value['result']:
                try:
                    result = json.loads(re.sub(r" \'([a-zA-Z]+)\' ",r" \1 ",str(value['result']))
                                    .replace('\', u', ', u').replace('u\'' , '').replace('\']', ']')
                                    .replace('`fi\'\\n', 'fi ').replace("don't", 'don^t').replace("'s ", '^s ')
                                    .replace('\': "', '\': \'').replace('", \'', '\', \'')
                                    .replace('\\\'', '').replace('\"', '^').replace('\'', '"')
                                    .replace('\\x1b', '').replace('\\n', '<br />').replace('\\', '')
                                    .replace('[1;31;40m', '<font color=red>').replace('[1;32;40m', '<font color=green>')
                                    .replace('[1;33;40m', '<font color=cyan>').replace('[1;34;40m', '<font color=blue>')
                                    .replace('[0m', '</font>'))
                except:
                    print "[ERROR] [json] task-id: " + str(value['uuid'])
                    result = ''
            else:
                result = ''
            timestamp = datetime.fromtimestamp(value['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            state = value['state']
            results.append({
                'uuid': uuid,
                'args': args,
                'group': args.split()[-1],
                'playbook': args.split()[-3],
                'result': result,
                'timestamp': timestamp,
                'state': state
            })
    return jsonify(results)


@ansibleplaybook.route('/os-init')
@login_required
def os_init():
    add_os_init_form = AddOsInitForm()
    return render_template('ansible_playbook/os_init.html', add_os_init_form=add_os_init_form)


@ansibleplaybook.route('/os-init-add', methods=['POST'])
@login_required
def os_init_add():
    form = AddOsInitForm(data=request.get_json())
    if form.validate_on_submit():
        hostlist = form.hostlist.data.split()
        host_list = [i.split(',')[0] for i in hostlist]
        ip_list = [ i.split(',')[-1] for i in hostlist ]
        update_inventory_temp(hostlist)
        playbook = os.path.join(Config.ANSIBLE_PATH, "S_os_init.yml")
        exec_command = str.format("{0} -i {1} --private-key={2} -e {3} {4} -l {5}", "ansible-playbook",
                                  Config.ANSIBLE_TEMP_INVENTORY_FILE, Config.ANSIBLE_KEY, ip_list, playbook, ":".join(host_list))
        print "ansible_playbook - " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " : " + exec_command
        task_result = celery_runner.ansible_playbook_task.apply_async([exec_command])
        result = {'r': 0, 'task_id': task_result.id, 'Location': url_for('.ansible_playbook_status', task_id=task_result.id)}
    else:
        result = {'r': 1, 'error': form.errors}
    return jsonify(result)


@ansibleplaybook.route('/get-playbook-vars')
@login_required
def get_playbook_vars():
    playbook = request.args.get('playbook')
    if playbook:
        result = get_ansible_playbook_vars(playbook)
        return jsonify(result)
    else:
        return jsonify({})


@ansibleplaybook.route('/ansible-playbook-temp')
@login_required
def ansible_playbook_temp():
    add_ansible_playbook_temp_form = AddAnsiblePlaybookTempForm()
    return render_template('ansible_playbook/ansible_playbook_temp.html', add_ansible_playbook_temp_form=add_ansible_playbook_temp_form)


@ansibleplaybook.route('/ansible-playbook-temp-add', methods=['POST'])
@login_required
def ansible_playbook_temp_add():
    form = AddAnsiblePlaybookTempForm(data=request.get_json())
    if form.validate_on_submit():
        hostlist = form.hostlist.data.split()
        host_list = [i.split(',')[0] for i in hostlist]
        update_inventory_temp(hostlist)
        playbook = os.path.join(Config.ANSIBLE_PATH, form.playbook.data)
        extra_var = form.extra_var.data
        exec_command = str.format("{0} -i {1} --private-key={2} --extra-vars \"{3}\" {4} -l {5}", "ansible-playbook",
                                  Config.ANSIBLE_TEMP_INVENTORY_FILE, Config.ANSIBLE_KEY, extra_var.strip(), playbook, ":".join(host_list))
        print "ansible_playbook - " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " : " + exec_command
        task_result = celery_runner.ansible_playbook_task.apply_async([exec_command])
        result = {'r': 0, 'task_id': task_result.id, 'Location': url_for('.ansible_playbook_status', task_id=task_result.id)}
    else:
        result = {'r': 1, 'error': form.errors}
    return jsonify(result)