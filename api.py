from flask_restful import Api, Resource, reqparse
import auth

class Auth(Resource):

    def post(self):
        users = input('Users: ')
        password = input('Password: ')
