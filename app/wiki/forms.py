# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import InputRequired
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    body = PageDownField("Enter your markdown", validators=[InputRequired()])
    submit = SubmitField('Submit')