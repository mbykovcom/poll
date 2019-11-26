import psycopg2

config = dict(
    NAME_DB='ddn6hou2602rtf',
    USER_DB='hfjwzwxsoqhdgk',
    PASSWORD_DB='a4fa52473856d9a2f4e96358d5ff357571c23c0271b9e068928a685efdebdf7e',
    HOST='ec2-23-21-70-39.compute-1.amazonaws.com',
    PORT=5432)


def connect_db():
    """
    Создает объект подключение к БД Postrges (данные берет из словаря config находится в данном модуле)
    и возваращет результат psycopg2.connect, если ошибка то False
    :return: psycopg2.connect
    """
    try:
        conn = psycopg2.connect(host=config['HOST'], dbname=config['NAME_DB'],
                                user=config['USER_DB'], password=config['PASSWORD_DB'],
                                port=config['PORT'])
        return conn
    except psycopg2.Error as err:
        print("Connection error: {}".format(err))
        return False


def add_answer_db(id, answers):
    """
    Добавляет варианты ответов в БД к заданной теме
    :param id: id темы
    :param answers: list вариантов ответов
    :return: None
    """
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
    """
    Обновляет варианты ответов в БД
    :param id: темы
    :param answers: list вариантов ответов
    :return: None
    """
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
