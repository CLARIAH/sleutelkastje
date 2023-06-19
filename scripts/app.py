# -*- coding: utf-8 -*-
import datetime
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
import json
import logging
import os
import psycopg2
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

app = Flask(__name__)
app.config.update({
    'OIDC_REDIRECT_URI' : os.environ.get('APP_DOMAIN', 'http://localhost') + '/test',
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


users = {
    "sysop": generate_password_hash("striktgeheim")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route("/hello")
@auth.login_required
def hello_world():
    return "Hello, {}!".format(auth.current_user())


@app.route('/add/appl=<app>,cred=<cred>,redir=<url>', methods=['POST'])
@auth.login_required
def add_app(app,cred,url):
    '''
    result = ''
    appl = ''
    cred = ''
    url = ''
    response = make_response(render_template('upload.html',app=app,credentials=cred,url=url),200)
    if request.method == 'POST':
        appl = request.form['app']
        cred = request.form['credentials']
        url = request.form['redirect']
'''
        # add app to database
    cur.execute('INSERT INTO application(mnemonic, credentials, redirect) VALUES (%s, %s, %s)',
            (app,cred,url))
    conn.commit()
    # if succesful:
    return make_response(render_template('succes.html',result=app),200)
#    return response


@app.route('/find/<app>', methods=['GET'])
def get_app(app):
    result = cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    response = make_response(render_template('get.html',result=result),200)
    #response.status = '200'
    #if request.method == 'GET':
        # reponse code ?
    #    response = make_response(render_template('get.html',result=app),201)
    return response

@app.route('/invite/<app>/<person>', methods=['POST'])
@oidc_auth.oidc_auth('default')
def invite(app,person):
    cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    res = cur.fetchone()
    cur.execute('INSERT INTO invitation(uuid, app) VALUES (%s, %s)',
            (person, res))
    conn.commit()
    response = make_response(render_template('invite.html',person=person,app=app),200)
    return response

@app.route('/test_login', methods=['GET'])
@oidc_auth.oidc_auth('default')
def test_inlog():
    user_session = UserSession(flask.session)
    
    userinfo = json.loads(user_session.userinfo.replace("'", "\""))
    stderr(f"eptid: {userinfo['edupersontargetedid']}")
    return jsonify(access_token=user_session.access_token,
                   id_token=user_session.id_token,
                   userinfo=user_session.userinfo)

@app.route('/register/<invite>', methods=['POST'])
@oidc_auth.oidc_auth('default')
def register(invite):
#    if not check_credentials(usr=eppn):
#        return make_response(render_template('not_allowed.html'),404)
    result = cur.execute("SELECT uuid,app FROM invitation WHERE _id = %s",[invite])
    # check result
    uuid,appl = cur.fetchone()
    cur.execute("SELECT mnemonic FROM application WHERE _id = %s",[appl])
    application = cur.fetchone()
    # 
    cur.execute('UPDATE users SET app = %s WHERE _id = %s',
            (appl,uuid,))
    # remove invite:
    cur.execute('DELETE FROM invitation WHERE _id = %s',[invite])
    conn.commit()
    response = make_response(render_template('accepted.html',person=uuid,app=app),200)
    return response

@app.route('/user/<usr>', methods=['POST'])
def add_user(usr):
    if not check_credentials(usr=eppn):
        return make_response(render_template('not_allowed.html'),404)
    cur.execute('INSERT INTO users(user_info) VALUES (%s)',[usr])
    conn.commit()
    response = make_response(render_template('new_user.html',usr=usr),200)
    return response

@app.route('/<app>/func,eppn=<eppn>', methods=['POST'])
@auth.login_required
def add_func_eppn(app,eppn):
    cur.execute('UPDATE application SET funcPerson = %s WHERE mnemonic = %s',[eppn,app])
    conn.commit()
    response = make_response(render_template('new_func.html',app=app,func=eppn),200)
    return response

@app.route('/<app>/func,eptid=<eptid>', methods=['POST'])
@auth.login_required
def add_func_eptid(app,eptid):
    cur.execute('UPDATE application SET funcPerson = %s WHERE mnemonic = %s',[eptid,app])
    conn.commit()
    response = make_response(render_template('new_func.html',app=app,func=eptid),200)
    return response

def stderr(text,nl='\n'):
    sys.stderr.write(f'{text}{nl}')



conn = None
cur = None
try:
    # read database configuration
    params = { 'host' : os.environ.get('DATABASE_HOST', 'localhost'),
                'port' : int(os.environ.get('DATABASE_PORT', 5432)),
                'database' : os.environ.get('DATABASE_DB', 'sleutelkastje'),
                'user' : os.environ.get('DATABASE_USER', 'test'),
                'password' : os.environ.get('DATABASE_PASSWORD', 'test') }
        
    stderr(params)
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
except Exception as e:
    stderr(f'connection to db failed:\n{e}')


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
#    auth.init_app(app)
    app.run()


