# coding: utf-8
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from ..jenkins_ext import jobs_list_get


class AddDeployForm(FlaskForm):
    module = SelectField('Module', coerce=str, validators=[DataRequired()])
    parameter = StringField('Parameter', validators=[DataRequired()])
    ops = SelectField('Ops', coerce=str, validators=[DataRequired()])
    result = TextAreaField('Parameter', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AddDeployForm, self).__init__(*args, **kwargs)
        self.module.choices = [(0, 'Choose...')] + [(i, i) for i in jobs_list_get()]
        self.ops.choices = [(0, 'Choose...'), ("admin", 'admin'), ("user", "user")]


class JenkinsExecForm(FlaskForm):
    job = SelectField('Select Exec Job', coerce=str, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(JenkinsExecForm, self).__init__(*args, **kwargs)
        self.job.choices = [(0, 'Choose...')] + [(i, i) for i in jobs_list_get()]