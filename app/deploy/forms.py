# coding: utf-8
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import input_required
from ..jenkins_ext import jobs_list_get


class AddDeployForm(FlaskForm):
    module = SelectField('Module', coerce=str, validators=[input_required()])
    parameter = StringField('Parameter', validators=[input_required()])
    ops = SelectField('Ops', coerce=str, validators=[input_required()])
    result = TextAreaField('Parameter', validators=[input_required()])

    def __init__(self, *args, **kwargs):
        super(AddDeployForm, self).__init__(*args, **kwargs)
        self.module.choices = [(0, 'Choose...')] + [(i, i) for i in jobs_list_get() ]
        self.ops.choices = [(0, 'Choose...'), ("admin", 'admin'), ("user", "user") ]