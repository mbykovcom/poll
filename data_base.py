import psycopg2

config = dict(
    NAME_DB='poll',
    USER_DB='poll',
    PASSWORD_DB='newpass',
    HOST='localhost')


def connect_db():
    try:
        conn = psycopg2.connect(host=config['HOST'], dbname=config['NAME_DB'],
                                user=config['USER_DB'], password=config['PASSWORD_DB'])
        return conn
    except psycopg2.Error as err:
        print("Connection error: {}".format(err))
        return False


def add_answer_db(id, answers):
    conn = connect_db()
    with conn.cursor() as cursor:
        for i in range(0, len(answers)):
                try:
                    cursor.execute('INSERT INTO choice (id_poll, answer)'
                                   'VALUES ({0},\'{1}\')'.format(id, answers[i]))
                except psycopg2.Error as e:
                    conn.rollback()
                    print(e)
                finally:
                    conn.commit()
    conn.close()


def update_answer_db(id, answers):
    conn = connect_db()
    with conn.cursor() as cursor:
        for i in range(0, len(answers)):
            try:
                cursor.execute('UPDATE choice '
                               'SET answer=\'{0}\''
                               'WHERE id={1}'.format(answers[i], id))
            except psycopg2.Error as e:
                conn.rollback()
                print(e)
            finally:
                conn.commit()
    conn.close()