# coding: utf-8
from flask import render_template, flash, Markup, redirect, url_for, abort
from flask_login import login_required
from . import wiki
from .forms import PostForm
from markdown import markdown
from config import Config
import os

wiki_dir = os.path.join(Config.BASE_DIR, 'wiki')


@wiki.route('/')
@login_required
def index():
    file_path = os.path.join(wiki_dir, 'index.md')
    if not os.path.isfile(file_path):
        abort(404)
    with open(file_path, 'r') as f:
        content = f.read().decode('utf-8').strip()

    content = Markup(markdown(content))
    return render_template('wiki/view.html', title='index', edit_url=url_for('.edit', name="index"),
                           content=content)


@wiki.route('/edit/<string:name>', methods=['GET', 'POST'])
@login_required
def edit(name):
    form = PostForm()
    file_path = os.path.join(wiki_dir, (name + '.md'))
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read().decode('utf-8').strip()
    else:
        content = ""

    if form.validate_on_submit():
        content = form.body.data.encode('utf-8').strip()
        with open(file_path, 'w') as f:
            f.write(content)
        flash('The wiki has been updated.')
        return redirect(url_for('.edit', name=name))

    form.body.data = content
    return render_template('wiki/edit.html', title=name, view_url=url_for('.view', name=name), form=form)


@wiki.route('/view/<string:name>')
@login_required
def view(name):
    file_path = os.path.join(wiki_dir, (name + '.md'))
    if not os.path.isfile(file_path):
        flash('Add new wiki: ' + name)
        return redirect(url_for('.edit', name=name))
        # abort(404)

    with open(file_path, 'r') as f:
        content = f.read().decode('utf-8').strip()
    content = Markup(markdown(content, extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.sane_lists']))
    return render_template('wiki/view.html', title=name, edit_url=url_for('.edit', name=name), content=content)