from flask import flash
import psycopg2
from data_base import connect_db


class Answer:
    """Класс ответов"""

    def __init__(self, id_user):
        """
        Создает объект Answer из БД. Содержит в себе всю информацию об ответах на опросы данного пользователя
        :param id_user: id пользователя
        """
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
        """
        Метод для получения всех ответов на опросы данного пользователя. Данные записывает в атрибут объекта answers
        :return: None
        """
        conn = connect_db()
        with conn.cursor() as cursor:
            try:
                cursor.execute('SELECT * FROM answer WHERE id_user={0}'.format(self._id_user))
                answers = cursor.fetchall()
            except psycopg2.Error as e:
                flash(e)
                return False
            finally:
                conn.close()

        for answer in answers:
            ans = [answer[0], answer[1], answer[3]]
            self._answers.append(ans)

    def vote(self, id_choice):
        """
        Метод добавления в БД ответа на опрос. Возвращает True - успешно, False - неудачно
        :param id_choice: id ответа
        :return: boll
        """
        print(self._answers)
        poll = []
        for ans in self._answers:
            poll.append(ans[1])
        conn = connect_db()
        # SELECT id_poll FROM choice WHERE id={0}.format(id_vote)
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id_poll FROM choice WHERE id={0}'.format(id_choice))
                result = cursor.fetchone()
                id_poll = result[0]
                if not id_poll in poll:
                    cursor.execute('INSERT INTO answer (id_poll, id_user, id_choice) '
                                   'VALUES ({0},{1},{2})'.format(id_poll, self._id_user, id_choice))
                else:
                    cursor.execute('UPDATE answer '
                                   'SET id_choice=\'{0}\''
                                   'WHERE id_poll={1} and id_user={2}'.format(id_choice, id_poll, self._id_user))
                conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            flash(e)
            return False
        finally:
            conn.close()
        return True


    @classmethod
    def countAnswer(cls, id_theme):
        """
        Метод подсчета всех ответов по заданной теме. Возвращает кол-во ответов на опрос
        :param id_theme: id темы
        :return: int
        """
        conn = connect_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(id) FROM answer WHERE id_poll={0}'.format(id_theme))
                count = cursor.fetchone()
        except psycopg2.Error as e:
            flash(e)
            return None
        finally:
            conn.close()
        return count[0]

    @classmethod
    def countChoice(cls, id_choice):
        """
        Метод подсчета всех ответов по заданной теме. Возвращает кол-во ответов на опрос
        :param id_choice: id ответа
        :return: int
        """
        conn = connect_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(id_user) FROM answer WHERE id_choice={0}'.format(id_choice))
                count = cursor.fetchone()
        except psycopg2.Error as e:
            flash(e)
            return None
        finally:
            conn.close()
        return count[0]

