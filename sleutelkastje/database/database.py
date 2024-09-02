import logging

import psycopg2

from sleutelkastje.application import Config

conn = None
cur = None

users = {
}

try:
    params = {
        'host': Config.DATABASE_HOST,
        'port': int(Config.DATABASE_PORT),
        'database': Config.DATABASE_DB,
        'user': Config.DATABASE_USER,
        'password': Config.DATABASE_PASSWORD,
    }

    logging.debug(params)
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
    cur.execute("SELECT * FROM application")
    result = cur.fetchall()
    # add to users
    for res in result:
        if not res[4] is None:
            users[res[1]] = {"password": res[2], "role": "funcbeh"}
            logging.debug(users[res[1]])
except Exception as e:
    logging.debug(f'connection to db failed:\n{e}')

