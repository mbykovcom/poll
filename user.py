from psycopg2 import errors
from flask import request, flash
from werkzeug.security import generate_password_hash

from data_base import connect_db


class User:

    """
    Класс пользователя
    """

    def __init__(self, login=None):
        """
        Создает нового пользователя. Если передан login то берет данного пользователя из БД
        :param login: Логин существуещего пользователя
        """
        self._login = login
        if self._login is not None:
            self.getUser()
        else:
            self._id_user = None
            self._name = None
            self.__password = None

    def __str__(self):
        """
        Получить данные пользователя
        :return: string
        """
        return 'Name: {0} | Login: {1} | Password: {2}'.format(self._name, self._login, self.__password)

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, id):
        if len(id) > 0:
            self._id_user = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if len(name) > 0:
            self._name = name

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, login):
        if len(login) > 0:
            self._login = login

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        if len(password) > 3:
            self.__password = password

    def create(self):
        """
        Добавляет пользователя в БД. Возвращает True - успешно, False - неудачно
        :return: boll
        """
        if self._name is not None and self._login is not None and self.__password is not None:

            if self.check_login():
                return False

            conn = connect_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO users (name ,login, password) '
                                   'VALUES (%s,%s,%s)', [self.name, self.login,
                                                         generate_password_hash(self.__password)])
                    conn.commit()
            except errors.InFailedSqlTransaction as e:
                flash(e)
                conn.rollback()
                return False
            finally:
                conn.close()
            return True
        else:
            flash('Ошибка! Не все поля заполнены')
            return False

    def check_login(self):
        """
        Проверяет существует ли пользователь с данным логином в БД. Возвращает True - существует, False - не существует
        :return: boll
        """
        if self._login is not None:
            conn = connect_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT login FROM users')
                    users = cursor.fetchall()
                    u = (self._login,)
                    if u in users:
                        flash('Ошибка! Логин занят!')
                        return True
            except errors as e:
                flash(e)
            finally:
                conn.close()
        else:
            flash('Ошибка! Логин не введен!')
            return True

    def getUser(self):
        """
        Воссоздает пользователя из БД по логину. Возвращает True - успешно, False - неудачно
        :return:
        """
        conn = connect_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE login=\'{0}\''.format(self._login))
                users = cursor.fetchone()
        except errors as e:
            flash(e)
            return False
        finally:
            conn.close()

        try:
            self._id_user = users[0]
            self._name = users[1]
            self.__password = users[3]
        except Exception as e:
            flash(e)
            return False
        return True
