from flask import jsonify, Response
from flask_restful import Api, Resource, reqparse
from auth import *
import user, poll as p


class Users(Resource):

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("login")
        parser.add_argument("password")
        params = parser.parse_args()
        u = user.User()
        u.name = params['name']
        u.login = params['login']
        u.password = params['password']
        if u.create():
            return Response('User was registered: {0}'.format(u), 200)
        elif u.name is None or u.login is None or u.password is None:
            return Response('Не все параметры переданы! | {0}'.format(u), 400)
        else:
            return Response('Логин {0} занят!'.format(u.login), 400)


class Polls(Resource):

    @auth.login_required
    def get(self, id = 0, theme=None):
        if id == 0 and theme is None:
            polls = p.Poll.getPolls()
            l = []
            for poll in polls.items():
                json = {}
                json['theme'] = poll[0]
                json['id_theme']=poll[1][0][0]
                ch = []
                for c in poll[1]:
                    ch.append({c[1]: c[2]})
                json['choice'] = ch
                l.append(json)
            return jsonify(l)
        elif id > 0:
            poll = p.Poll.getPoll(id=id)
        elif theme is not None:
            poll = p.Poll.getPoll(theme=theme)
        else:
            return Response('Некорерктный id: {0} !'.format(id), 400)
        if poll:
            json = {}
            json['theme'] = poll.theme
            json['id_theme'] = poll.id_theme
            ch = []
            for c in poll.answers.items():
                ch.append({c[0]: c[1]})
            json['choice'] = ch
            return jsonify(json)
        else:
            return Response('Темы с таким id: {0} не существует!'.format(id), 400)


    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("theme")
        parser.add_argument("answer")
        params = parser.parse_args()
        answers = params['answer'].split(',')
        for i in range(0, len(answers)):
            answers[i] = answers[i].strip()
        poll = p.Poll()
        poll.theme = params['theme']
        poll.answers = answers
        if not poll.getId():
            if len(poll.answers) > 1 and poll.create():
                return Response('Опрос добавлен!', 200)
            else:
                return Response('Bad Request! Проверьте данные, передаваемые в теле', 400)
        else:
            return Response('Ошибка! Тема с таким названием уже существует!', 400)


