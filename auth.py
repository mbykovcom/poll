import data_base
from werkzeug.security import check_password_hash
from flask import Response, request
from functools import wraps



def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """

    if len(username) > 0:
        conn = data_base.connect_db()
        with conn.cursor() as cursor:
            cursor.execute('Select login, password ' \
                           'From users ' \
                           'Where login=\'{0}\''.format(username))
            records = cursor.fetchone()
            conn.close()
            if records is not None and username in records[0]:
                return check_password_hash(records[1], password)

    return False


def authenticate():
    """
    Response 401
    """

    return Response(
        'ERROR 401: Вы должны войти в систему с соответствующими учетными данными', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated