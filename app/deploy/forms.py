# coding: utf-8
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from ..jenkins_ext import jobs_list_get


class AddDeployForm(FlaskForm):
    module = SelectField('Module', coerce=str, validators=[DataRequired()])
    deploy_dir = StringField('Deploy_dir', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AddDeployForm, self).__init__(*args, **kwargs)
        self.module.choices = [(0, 'Choose...')] + [(i, i) for i in jobs_list_get()]


class JenkinsExecForm(FlaskForm):
    job = SelectField('Select Exec Job', coerce=str, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(JenkinsExecForm, self).__init__(*args, **kwargs)
        self.job.choices = [(0, 'Choose...')] + [(i, i) for i in jobs_list_get()]