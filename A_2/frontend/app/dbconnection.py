import mysql.connector
from app.config import db_config
from datetime import datetime
from flask import g


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])


def get_image(key):
    cnx = get_db()

    cursor = cnx.cursor()
    query = "SELECT path FROM image WHERE ID = %s;"
    cursor.execute(query, (key,))

    return cursor


def put_image(key, path):
    cnx = get_db()

    cursor = cnx.cursor()
    query = "INSERT INTO image (ID, path, last_edited_time) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE path = %s, last_edited_time = %s;"
    cursor.execute(query, (key, path, datetime.now(), path, datetime.now()))

    cnx.commit()


def list_keys():
    cnx = get_db()

    cursor = cnx.cursor()
    query = "SELECT ID FROM image;"
    cursor.execute(query)

    return cursor


def put_config(capacity, policy):
    cnx = get_db()

    cursor = cnx.cursor()
    query = "INSERT INTO memcache_config (updated_time, capacity, policy) VALUES (%s, %s, %s);"
    cursor.execute(query, (datetime.now(), capacity, policy))

    cnx.commit()


def put_mode(num_node, mode, max_thr, min_thr, expand_ratio, shrink_ratio):
    cnx = get_db()

    cursor = cnx.cursor()
    query = "INSERT INTO memcache_mode (updated_time, num_node, mode, max_thr, min_thr, expand_ratio, shrink_ratio) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(query, (datetime.now(), num_node, mode, max_thr, min_thr, expand_ratio, shrink_ratio))

    cnx.commit()


def clear():
    cnx = get_db()

    cursor = cnx.cursor()
    query = "DELETE FROM image;"
    cursor.execute(query)

    cnx.commit()


def update_image(key):
    cnx = get_db()

    cursor = cnx.cursor()
    query = "UPDATE image SET last_edited_time = %s WHERE ID = %s;"
    cursor.execute(query, (datetime.now(), key))

    cnx.commit()


def sort_by_time(key_list):
    cnx = get_db()

    ids_to_sort = ', '.join(str(id) for id in key_list)

    cursor = cnx.cursor()
    query = "SELECT ID FROM image WHERE ID IN ({ids}) ORDER BY last_edited_time;"
    cursor.execute(query.format(ids=ids_to_sort))

    return cursor