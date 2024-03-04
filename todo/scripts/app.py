# -*- coding: utf-8 -*-
import datetime
import functools
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
import logging
import os
#import psycopg2
import requests
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


def oidc_or_header_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if oidc_auth and 'Authorization' not in request.headers:
            return oidc_auth.oidc_auth('default')(func)(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper


@app.route("/hello")
def hello_world():
    return "Hello, world!"



@app.route('/todo', methods=['GET'])
@oidc_or_header_auth
def get_app():
    # we won't use eptid
    #eptid = ''
    eppn = ''
    user_session = UserSession(flask.session, 'default')
    if user_session.last_authenticated is not None:
        userinfo = user_session.userinfo
        #eptid = userinfo['edupersontargetedid'][0]
        #TODO: al ingelogd betekent niet dat deze gebruiker ook deze app mag gebruiken...
        eppn = userinfo['eppn'][0]
    else:
        token = request.headers['Authorization'].replace("Bearer","").strip()
        logging.debug(f'token: {token}')
        response = requests.post('https://sleutelkast.sd.di.huc.knaw.nl/todo', auth=('todo', 'ookgeheim'), data={"key":token})
        #eptid = response.json()['edupersontargetedid'][0]
        eppn = response.json()['eppn'][0]
    #logging.debug(f'eptid: {eptid}')
    logging.debug(f'eppn: {eppn}')
    response = ''
    #try:
        #with open(f'{todofiles}/{eptid}.todo') as todo:
            #response = make_response(''.join(todo.readlines()),200)
    #except:
    try:
        with open(f'{todofiles}/{eppn}.todo') as todo:
            response = make_response(''.join(todo.readlines()),200)
    except:
        response =  make_response('No todo file, enjoy your day!',200)
    return response

@app.route('/test_login', methods=['GET'])
#@oidc_auth.oidc_auth('default')
def test_inlog():
    try:
        user_session = UserSession(flask.session)
        userinfo = user_session.userinfo
        #stderr(f"eptid: {userinfo['edupersontargetedid']}")
        stderr(f"eppn: {userinfo['eppn']}")
        return jsonify(access_token=user_session.access_token,
                    id_token=user_session.id_token,
                    userinfo=user_session.userinfo)
    except:
        print("todo app: except")
        # curl etc ?
        
        token = 'huc:>j~|6,G$o.<lo0zf'
        headers = { 'Authorization': f'bearer {token}' }
        response = requests.post('https://sleutelkast.sd.di.huc.knaw.nl/todo', headers=headers)
        print(response)
#        response = 'check for the API token'

        #TODO: check if there is a bearer token in the Authentication header
        #TODO: if so check the token with sleutelkastje using <sleutelkast>/<appl>/<key>
        #TODO: if valid: return the userinfo you get back from sleutelkastje else unauthorized
        return jsonify(response=response.text)

def stderr(text,nl='\n'):
    sys.stderr.write(f'{text}{nl}')


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
todofiles = 'todofiles'
if not os.path.exists(todofiles):
    os.mkdir(todofiles)

if __name__ == "__main__":
#    auth.init_app(app)
    app.run()


