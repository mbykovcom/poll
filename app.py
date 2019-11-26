#!/usr/bin/python
from functools import wraps

from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug import exceptions
from auth import *
import user
import poll as p
import answer
from flask_restful import Api
import api.api as api_app
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'development key'

conn = data_base.connect_db()

api.add_resource(api_app.Users, '/api/user_add')
api.add_resource(api_app.Polls, '/api/polls', '/api/poll/', '/api/poll/<int:id>', '/api/poll/<string:theme>',
                                '/api/add_poll')


@app.route('/')
def index():
    if request.authorization is not None:
        if request.authorization.username == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('voting_page'))
    else:
        return render_template('index.html')


@app.route('/login')
@auth.login_required
def login():
    if request.authorization is not None and 'admin' == request.authorization.username:
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('index'))


@app.route('/registration')
def show_registration():
    return render_template('registration.html', data=[])


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
@auth.login_required
def admin_panel():
    polls = p.Poll.getPolls()
    return render_template('admin_panel.html', polls=polls)


@app.route('/add_poll')
@auth.login_required
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
@auth.login_required

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
@auth.login_required

def show_edit_poll(id_poll):
    if not request.authorization.username == 'admin':
        return redirect(url_for('index'))

    poll = p.Poll.getPoll(id_poll)
    return render_template('edit_poll.html', poll=poll)


@app.route('/edit_poll/<int:id_poll>', methods=['POST'])
@auth.login_required

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
@auth.login_required

def delete_poll(id_poll):
    if not request.authorization.username == 'admin':
        return redirect(url_for('index'))

    poll = p.Poll(id_poll)
    if poll.delete():
        flash('Опрос был удален!')
    return redirect(url_for('index'))


@app.route('/voting_page')
@auth.login_required

def voting_page():
    polls = p.Poll.getPolls()
    u = user.User(request.authorization.username)
    answer_user = answer.Answer(u.id_user)
    count = {}
    for pl in polls.items():
        sum = 0
        ans = {}
        for item in pl[1]:
            c = answer.Answer.countChoice(item[1])
            sum += c
            ans[item[1]] = answer.Answer.countChoice(item[1])
        ans['sum']=sum
        count[pl[1][0][0]] = ans
    return render_template('voting_page.html', polls=polls, answers=answer_user.answers, count=count)


@app.route('/voting_page', methods=['POST'])
@auth.login_required
def vote():
    u = user.User(request.authorization.username)
    choice = answer.Answer(u.id_user)
    choice.vote(request.form['options'])
    print(answer.Answer(u.id_user).answers)
    return redirect(url_for('voting_page'))



if __name__ == '__main__':
    app.run(debug=True)
