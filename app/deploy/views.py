# coding: utf-8
from flask import render_template, redirect, request, url_for, flash, \
    jsonify
from flask_login import login_required, current_user
from . import deploy
from .. import flash_errors
from .forms import AddDeployForm, JenkinsExecForm
from ..jenkins_ext import jobs_list_get, job_build


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


@deploy.route('/deploy-history')
@login_required
def deploy_history():
    return render_template('deploy/deploy_history.html')