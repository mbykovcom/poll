from flask import flash
from psycopg2 import errors

from data_base import connect_db


class Answer:

    def __init__(self, id_user):
        if int(id_user) > 0:
            self._id_user = int(id_user)
            self._answers = []
            self.getAnswers()

    @property
    def id_user(self):
        return self._id_user

    @property
    def answers(self):
        return self._answers

    def getAnswers(self):
        conn = connect_db()
        with conn.cursor() as cursor:
            try:
                cursor.execute('SELECT * FROM answer WHERE id_user={0}'.format(self._id_user))
                answers = cursor.fetchall()
            except errors as e:
                flash(e)
                return False
            finally:
                conn.close()

        for answer in answers:
            ans = [answer[0], answer[1], answer[3]]
            self._answers.append(ans)
