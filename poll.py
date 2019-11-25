from flask import flash
from psycopg2 import errors, Error

from data_base import connect_db, add_answer_db, update_answer_db


class Poll:

    def __init__(self, id_poll=None):
        self._id_theme = id_poll
        if self._id_theme is not None:
            p = self.getPoll(self._id_theme)
            self._theme = p.theme
            self._answers = p.answers
            self._new_answers = p.new_answers
        else:
            self._theme = None
            self._answers = None
            self._new_answers = None

    @property
    def id_theme(self):
        return self._id_theme

    @id_theme.setter
    def id_theme(self, id):
        if id > 0:
            self._id_theme = id

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        self._theme = theme

    @property
    def answers(self):
        return self._answers

    @answers.setter
    def answers(self, answers):
        if len(answers) > 0:
            self._answers = answers

    @property
    def new_answers(self):
        return self._new_answers

    @new_answers.setter
    def new_answers(self, new_answers):
        if len(new_answers) > 0:
            self._new_answers = new_answers

    def getId(self):
        if self._theme is not None:
            conn = connect_db()
            with conn.cursor() as cursor:
                cursor.execute('SELECT id FROM poll WHERE theme=\'{0}\''.format(self._theme))
                id = cursor.fetchone()
            conn.close()
            self._id_theme = id[0]
        else:
            flash('Ошибка! Тема не задана!')

    def checkPoll(self):
        if self._theme is not None:
            conn = connect_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT theme FROM poll')
                    polls = cursor.fetchall()
                    t = (self._theme,)
                    if t in polls:
                        flash('Ошибка! Опрос с такой темой уже существует!')
                        return True
            except errors as e:
                flash(e)
            finally:
                conn.close()
        else:
            flash('Ошибка! Тема не задана!')
            return True

    def create(self):
        if self._theme is not None and self._answers is not None:
            if self.checkPoll():
                return False
            conn = connect_db()
            with conn.cursor() as cursor:
                try:
                    cursor.execute('INSERT INTO poll(theme) '
                                   'VALUES (\'{0}\')'.format(self._theme))
                    conn.commit()
                    if self._id_theme is None:
                        self.getId()
                    add_answer_db(self._id_theme, self._answers)
                    if self._new_answers is not None:
                        add_answer_db(self._id_theme, self._new_answers)
                    conn.commit()
                    return True
                except Error as e:
                    conn.rollback()
                    flash(e)
                except BaseException as e:
                    conn.rollback()
                    flash(e)
                finally:
                    conn.close()

    def edit(self, theme=None, answer=None, new_answer=None):
        conn = connect_db()
        if self._id_theme is None:
            self.getId()
        if theme is not None and self._theme != theme:
            self._theme = theme
        if answer is not None:
            i = 0
            for item in self._answers.items():
                if item[1] != answer[i]:
                    self._answers[item[0]] = answer[i]
                i += 1
        with conn.cursor() as cursor:
            cursor.execute('UPDATE poll '
                           'SET theme=\'{0}\''
                           'WHERE id={1}'.format(self._theme, self._id_theme))
            for item in self.answers.items():
                cursor.execute('UPDATE choice '
                               'SET answer=\'{0}\''
                               'WHERE id={1}'.format(item[1], item[0]))
            conn.commit()
        conn.close()
        if new_answer is not None:
            add_answer_db(self._id_theme, new_answer)
        return True

    def delete(self):
        if self._id_theme is not None:
            conn = connect_db()
            with conn.cursor() as cursor:
                try:
                    cursor.execute('DELETE FROM poll WHERE id=%i' % self._id_theme)
                    conn.commit()
                    return True
                except errors as e:
                    conn.rollback()
                    flash(e)
                    return False
                finally:
                    conn.close()
        elif self._theme is not None:
            self.getId()
            self.delete()
        else:
            flash('Ошибка! Не хватает информации для операции.\n Укажите объекту id или тему.')

    @classmethod
    def getPolls(cls):
        conn = connect_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM poll ORDER BY id desc')
            topics = cursor.fetchall()
            cursor.execute('SELECT * FROM choice')
            answers = cursor.fetchall()
            polls = {}
            for i in range(0, len(topics)):
                ar = []
                for answer in answers:
                    if topics[i][0] == answer[1]:
                        ar.append([answer[1], answer[0], answer[2]])
                polls[topics[i][1]] = ar
        conn.close()
        return polls

    @classmethod
    def getPoll(cls, id):
        conn = connect_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT poll.id, theme, choice.id, answer '
                           'FROM poll '
                           'INNER JOIN choice ON poll.id=choice.id_poll '
                           'WHERE poll.id={0}'.format(id))
            p = cursor.fetchall()
            poll = Poll()
            poll._id_theme = p[0][0]
            poll._theme = p[0][1]
            answer = {}
            for ans in p:
                answer[ans[2]] = ans[3]
            poll._answers = answer
        conn.close()
        return poll

