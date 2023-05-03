# -*- coding: utf-8 -*-
from config import config
import datetime
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
import logging
import os
import psycopg2
import sys

from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

app = Flask(__name__)

app.config.update({'OIDC_REDIRECT_URI': 'https://aboutme.diginfra.net/oauth2/redirect',
                   'SECRET_KEY': 'dev_key',  # make sure to change this!!
                   'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=7).total_seconds(),
                   'DEBUG': True})

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/add/<app>', methods=['GET','POST'])
def add_app(app):
    result = ''
    appl = ''
    cred = ''
    url = ''
    response = make_response(render_template('upload.html',app=app,credentials=cred,url=url),200)
    if request.method == 'POST':
        appl = request.form['app']
        cred = request.form['credentials']
        url = request.form['redirect']
        # add app to database
        cur.execute('INSERT INTO application(mnemonic, credentials, redirect) VALUES (%s, %s, %s)',
            (appl,cred,url))
        conn.commit()
        return make_response(render_template('succes.html',result=appl),200)
    return response


@app.route('/find/<app>', methods=['GET'])
def get_app(app):
    result = ''
    filename = ''
    response = make_response(render_template('get.html',result=result),200)
    #response.status = '200'
    if request.method == 'GET':
        # reponse code ?
        response = make_response(render_template('get.html',result=app),201)
    return response

@app.route('/invite/<app>/<person>', methods=['POST'])
def invite(app,person):
    cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    res = cur.fetchone()
    cur.execute('INSERT INTO invitation(uuid, app) VALUES (%s, %s)',
            (person, res))
    conn.commit()
    response = make_response(render_template('invite.html',person=person,app=app),200)
    return response

@app.route('/accept/<invite>', methods=['POST'])
def accept(invite):
    cur.execute("SELECT uuid,app FROM invitation WHERE _id = %s",[invite])
    uuid,appl = cur.fetchone()
    cur.execute("SELECT mnemonic FROM application WHERE _id = %s",[appl])
    application = cur.fetchone()
    cur.execute('UPDATE users SET app = %s WHERE _id = %s',
            (appl,uuid,))
    cur.execute('DELETE FROM invitation WHERE _id = %s',[invite])
    conn.commit()
    response = make_response(render_template('accepted.html',person=uuid,app=app),200)
    return response

@app.route('/user/<usr>', methods=['POST'])
def add_user(usr):
    cur.execute('INSERT INTO users(user_info) VALUES (%s)',[usr])
    conn.commit()
    response = make_response(render_template('new_user.html',usr=usr),200)
    return response


def stderr(text,nl='\n'):
    sys.stderr.write(f'{text}{nl}')

if __name__ == "__main__":

    conn = None
    cur = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
    except Exception as e:
        stderr(f'connection to db failed:\n{e}')


    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#    auth.init_app(app)
    app.run()

