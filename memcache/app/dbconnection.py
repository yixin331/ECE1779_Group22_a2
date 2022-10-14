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


def show_stat():
    cnx = get_db()

    cursor = cnx.cursor()
    query = "SELECT * FROM memcache_stat WHERE updated_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE);"
    cursor.execute(query)

    return cursor


def put_stat(num_item, total_size, num_request, num_get, num_miss):
    cnx = get_db()

    cursor = cnx.cursor()
    if num_get == 0:
        query = "INSERT INTO memcache_stat (updated_time, num_item, total_size, num_request, miss_rate, hit_rate) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (datetime.now(), num_item, total_size, num_request, 0, 0))
    else:
        query = "INSERT INTO memcache_stat (updated_time, num_item, total_size, num_request, miss_rate, hit_rate) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (datetime.now(), num_item, total_size, num_request, num_miss/num_get, (num_get- num_miss)/num_get))

    cnx.commit()
