# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, InputRequired
from ..ansible_ext import get_inventory_group


class AddAnsibleForm(FlaskForm):
    group = SelectField('Group', coerce=str, validators=[DataRequired()])
    host = StringField('Host', validators=[DataRequired()])
    user = SelectField('User', coerce=str, validators=[DataRequired()])
    command = StringField('Command', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AddAnsibleForm, self).__init__(*args, **kwargs)
        self.group.choices = [(0, 'Choose...')] + [(i, i) for i in get_inventory_group() if i != "all:vars" ] + [('all', 'all')]
        self.user.choices = [('apprun', 'apprun'), ('root', 'root')]