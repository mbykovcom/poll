import data_base
from werkzeug.security import check_password_hash
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
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

