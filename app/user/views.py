# coding: utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, UserMixin
from . import user
from .forms import LoginForm
from .. import login_manager


users = {'admin': {'password': 'admin123'}}


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    user.username = username
    return user


@login_manager.user_loader
def get_user(username):
    if username not in users:
        return

    user = User()
    user.id = username
    user.username = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    if request.form['password'] == users[username]['password']:
        return user
    else:
        return None


@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        if username is not None and users[username]['password'] == form.password.data:
            user = User()
            user.id = username
            user.username = username
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))