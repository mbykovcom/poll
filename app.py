#!/usr/bin/python
from functools import wraps

from flask import Flask, request, render_template, url_for, redirect, flash, jsonify
from werkzeug import exceptions
import psycopg2
import data_base, auth
import user
import poll as p
import answer
from flask_restful import Api, Resource, reqparse
import api as api_app

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'development key'

conn = data_base.connect_db()

api.add_resource(api_app.Auth, '/api/login')


# api.add_resource(TodoSimple, '/api/<string:todo_id>')
# api.add_resource(TodoSimple, '/api/<string:todo_id>')
# api.add_resource(TodoSimple, '/api/<string:todo_id>')


@app.route('/')
def index():
    if request.authorization is not None:
        if request.authorization.username == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('voting_page'))
    else:
        return render_template('index.html')

#
# @app.route('/api/login?<login>&<password>', methods=['POST'])
# def api_index(login, password):
#     print(login, password)
#     return jsonify(login, password)


@app.route('/login')
@auth.requires_auth
def login():
    if request.authorization.username == 'admin':
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('voting_page'))


@app.route('/logout')
def logout():
    if request.authorization:
        return auth.authenticate()
    else:
        return redirect(url_for('index'))


@app.route('/registration')
def show_registration():
    return render_template('registration.html', data=[])


# Повесить валидацию?
@app.route('/registration', methods=['POST'])
def registration():
    u = user.User()
    u.name = request.form['name']
    u.login = request.form['login']
    u.password = request.form['password']

    if u.create():
        return redirect(url_for('index'))
    else:
        data = [u.name, u.login]
        return render_template('registration.html', data=data)


@app.route('/admin')
@auth.requires_auth
def admin_panel():
    if request.authorization.username != 'admin':
        return redirect(url_for('index'))
    polls = p.Poll.getPolls()
    return render_template('admin_panel.html', polls=polls)


@app.route('/add_poll')
@auth.requires_auth
def show_add_poll():
    if request.authorization.username == 'admin':
        return render_template('add_poll.html')
    else:
        return redirect(url_for('index'))


def validation_form(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        mess = 'Ошибка! ' \
               'Не все поля заполнены!'
        if request.form['theme'] == '':
            flash(mess)
            return redirect(url_for('admin_panel'))
        answer = request.form.getlist('answer')
        for ans in answer:
            if ans == '':
                flash(mess)
                return redirect(url_for('admin_panel'))
        answer = request.form.getlist('new_answer')
        for ans in answer:
            if ans == '':
                flash(mess)
                return redirect(url_for('admin_panel'))
        return f(*args, **kwargs)

    return decorated


@app.route('/add_poll', methods=['POST'])
@auth.requires_auth
@validation_form
def add_poll():
    if not request.authorization.username == 'admin':
        return redirect(url_for('index'))

    poll = p.Poll()
    poll.theme = request.form['theme']
    poll.answers = request.form.getlist('answer')
    poll.new_answers = request.form.getlist('new_answer')
    if poll.create():
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('index'))


@app.route('/edit_poll/<int:id_poll>')
@auth.requires_auth
def show_edit_poll(id_poll):
    if not request.authorization.username == 'admin':
        return redirect(url_for('index'))

    poll = p.Poll.getPoll(id_poll)
    return render_template('edit_poll.html', poll=poll)


@app.route('/edit_poll/<int:id_poll>', methods=['POST'])
@auth.requires_auth
@validation_form
def edit_poll(id_poll):
    poll = p.Poll.getPoll(id_poll)
    theme = request.form['theme']
    answer = request.form.getlist('answer')
    try:
        new_answer = request.form['new_answer']
    except exceptions.BadRequestKeyError:
        new_answer = None
    poll.edit(theme, answer, new_answer)
    return redirect(url_for('admin_panel'))


@app.route('/delete_poll/<int:id_poll>')
@auth.requires_auth
def delete_poll(id_poll):
    if not request.authorization.username == 'admin':
        return redirect(url_for('index'))

    poll = p.Poll(id_poll)
    if poll.delete():
        flash('Опрос был удален!')
    return redirect(url_for('index'))


@app.route('/voting_page')
@auth.requires_auth
def voting_page():
    polls = p.Poll.getPolls()
    u = user.User(request.authorization.username)
    ans = answer.Answer(u.id_user)
    poll = polls.items()
    for pl in poll:
        for id in pl[1]:
            for an in ans.answers:
                print(id[1] == an[2])
    print(ans.answers)
    return render_template('voting_page.html', polls=polls, answers=ans.answers)


if __name__ == '__main__':
    app.run(debug=True)
