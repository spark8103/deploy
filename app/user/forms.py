# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, Regexp, input_required


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 64),
                                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                   'Usernames must have only letters, '
                                                   'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[input_required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')