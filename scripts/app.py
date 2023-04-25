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
        # 
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


