# -*- coding: utf-8 -*-
import datetime
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
import logging
import os
#import psycopg2
import secrets
import string
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

app = Flask(__name__)
app.config.update({
    'OIDC_REDIRECT_URI' : os.environ.get('APP_DOMAIN', 'http://localhost') + '/oauth2/redirect',
    'SECRET_KEY' : os.environ.get('SECRET_KEY', uuid.uuid4().hex),
    'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=7).total_seconds(),
                   'DEBUG': True})
auth = HTTPBasicAuth()

oidc_auth = OIDCAuthentication({'default': ProviderConfiguration(
    issuer=os.environ['OIDC_SERVER'],
    client_metadata=ClientMetadata(
        client_id=os.environ['OIDC_CLIENT_ID'],
        client_secret=os.environ['OIDC_CLIENT_SECRET']),
    auth_request_params={'scope': ['openid', 'email', 'profile'],
        'claims': {"userinfo":{"edupersontargetedid":None,"schac_home_organisation":None,"nickname":None,"email":None,"eppn":None,"idp":None}}})}, app) if 'OIDC_SERVER' in os.environ and len(os.environ['OIDC_SERVER']) > 0 else None



@app.route("/hello")
def hello_world():
    return "Hello, world!"



@app.route('/todo', methods=['GET'])
@oidc_auth.oidc_auth('default')
def get_app():
    user_session = UserSession(flask.session)
    userinfo = user_session.userinfo
    eptid = userinfo['edupersontargetedid']
    stderr(f"eptid: {eptid}")
    response = ''
    try:
        with open(f'{todofiles}/{eptid}.todo') as todo:
            reponse = make_response(''.join(todo.readlines()),200)
    except:
        reponse =  make_response('No todo file, enjoy your day!',200)
    stderr(f'resonse: {response}')
    return response

@app.route('/test_login', methods=['GET'])
@oidc_auth.oidc_auth('default')
def test_inlog():
    user_session = UserSession(flask.session)
    userinfo = user_session.userinfo
    stderr(f"eptid: {userinfo['edupersontargetedid']}")
    return jsonify(access_token=user_session.access_token,
                   id_token=user_session.id_token,
                   userinfo=user_session.userinfo)


def stderr(text,nl='\n'):
    sys.stderr.write(f'{text}{nl}')


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
todofiles = 'todofiles'
if not os.path.exists(todofiles):
    os.mkdir(todofiles)

if __name__ == "__main__":
#    auth.init_app(app)
    app.run()


