# -*- coding: utf-8 -*-
import datetime
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
import json
import logging
import os
import psycopg2
import re
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
        "sysop": { "password": generate_password_hash("striktgeheim"), "role": "sysop"}
}

#TODO 20240304: the apps, e.g., todo, should be loaded from the database and their <app>,<cred> added to the users dictionary
# this is done below after connecting to the database

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username)["password"], password):
        return username

@auth.get_user_roles
def get_user_roles(user):
    return users[user]['role']

@app.route("/hello")
@auth.login_required
def hello_world():
    return "Hello, {}!".format(auth.current_user())


# 1. register app
@app.route('/add/appl=<app>,cred=<cred>,redir=<url>', methods=['POST'])
@auth.login_required(role='sysop')
def add_app(app,cred,url):
    #TODO: check that logged in user is sysop
    logging.debug(f'add app[{app}] - cred[{cred}] - url[{url}]')
    # add app to database
    cur.execute('INSERT INTO application(mnemonic, credentials, redirect) VALUES (%s, %s, %s)',
            (app,generate_password_hash(cred),url))
    conn.commit()
    #TODO 20240304: add <app>, generate_password_hash(<cred>) also to users dictionary
    users[app] = { "password": generate_password_hash(cred), "role": "funcbeh"}
    return make_response(render_template('succes.html',result=app),200)


@app.route('/find/<app>', methods=['GET'])
def get_app(app):
    logging.debug(f'get app[{app}]')
    result = cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    response = make_response(render_template('get.html',result=result),200)
    return response

def is_func(app,eppn):
    #TODO 20240304: check if the <eppn> is from the funcbeh of <app>, return true if so otherwise false
    cur.execute("SELECT funcPerson FROM application WHERE mnemonic = %s",[app])
    func_person = cur.fetchone()
    if func_person is None:
        return False
    func_person = func_person[0]
    logging.debug(f'fp: {func_person} ({eppn==func_person})')
    return eppn == func_person

# 3. user invited 
@app.route('/invite/<app>', methods=['GET'])
@oidc_auth.oidc_auth('default')
def invite(app):
    # TODO: check if it's the functioneel beheerder die deze invite maakt
    # 1. haal de func beheerder van <app> uit de db
    # 2. vergelijk die met degene die deze invite uitvoert
    # 3. kijk of de role wel 'funcbeh' is
    user_session = UserSession(flask.session)
    userinfo = user_session.userinfo
    if not is_func(app,userinfo['eppn'][0]):
        # TODO 20240304: return unauthorized
        return make_response('unauthorized',401)
    uuid = get_invite()
    logging.debug(f'app[{app}] invite[{uuid}]')
    cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    app_id = cur.fetchone()
    cur.execute('INSERT INTO invitation(uuid, app) VALUES (%s, %s)',
            (uuid, app_id))
    conn.commit()
    response = make_response(render_template('invite.html',invite=uuid,app=app),200)
    return response

def get_api_key(length=16):
    key = ''
    for i in range(length):
        key += ''.join(secrets.choice(alphabet))
    return f'huc:{key}'

def get_invite(length=8):
    key = ''
    for i in range(length):
        key += ''.join(secrets.choice(letters + digits))
    return key

# 4. user registers
@app.route('/register/<invite>', methods=['GET'])
@oidc_auth.oidc_auth('default')
def register(invite):
    logging.debug(f'register invite[{invite}]')
#    if not check_credentials(usr=eppn):
#        return make_response(render_template('not_allowed.html'),404)
    user_session = UserSession(flask.session)
    userinfo = user_session.userinfo
    userinfo_str = json.dumps(userinfo)

    cur.execute("SELECT _id,uuid,app,usr FROM invitation WHERE uuid = %s",[invite])
    # check result
    inv_id,uuid,appl_id,usr_id = cur.fetchone()
    if usr_id!=None:
        return "Invitation has been used"

    # maak een nieuwe user aan en sla de user info op als JSON -> usr_id
    cur.execute('INSERT INTO users(user_info) VALUES (%s)', (userinfo_str,))
    cur.execute('SELECT LASTVAL()')
    user_id = cur.fetchone()[0]
    logging.debug(f'new user_id: {user_id}')

    # connect invite to user:
    cur.execute('UPDATE invitation SET usr = %s WHERE _id = %s',[user_id,inv_id])
    conn.commit()
    # 5. make api_key
    api_key = get_api_key()
    cur.execute('INSERT INTO key(key, usr) VALUES (%s, %s)', (api_key, user_id))
    conn.commit()
    eppn = userinfo['eppn'][0]
    cur.execute("SELECT mnemonic FROM application WHERE _id = %s",[appl_id])
    # check result
    appl = cur.fetchone()[0]
    response = make_response(render_template('accepted.html',person=eppn,app=appl,key=api_key),200)
    return response


@app.route('/user/<usr>', methods=['POST'])
@oidc_auth.oidc_auth('default')
def add_user(usr):
    if not check_credentials(usr=eppn):
        return make_response(render_template('not_allowed.html'),404)
    cur.execute('INSERT INTO users(user_info) VALUES (%s)',[usr])
    conn.commit()
    response = make_response(render_template('new_user.html',usr=usr),200)
    return response

# 2. app gets a functioneel beheerder (with eppn)
@app.route('/<app>/func,eppn=<eppn>', methods=['POST'])
#TODO: check that logged in user is sysop
@auth.login_required(role='sysop')
def add_func_eppn(app,eppn):
    logging.debug(f'add functioneel beheerder eppn[{eppn}] to app[{app}]')
    try:
        cur.execute('UPDATE application SET funcPerson = %s WHERE mnemonic = %s',[eppn,app])
        conn.commit()
    except errors.InFailedSqlTransaction as err:
        logging.debug(f'error in update: {err}')
    
    # what if app does not exists ?
    response = make_response(render_template('new_func.html',app=app,func=eppn),200)
    return response

# 2. app gets a functioneel beheerder (with eptid)
# We won't use eptid (for the forseable future
#@app.route('/<app>/func,eptid=<eptid>', methods=['POST'])
#@auth.login_required
#def add_func_eptid(app,eptid):
    #TODO: check that logged in user is sysop
    #if auth.current_user()['role']=='sysop':
        #logging.debug(f'add functioneel beheerder eptid[{eptid}] to app[{app}]')
        #cur.execute('UPDATE application SET funcPerson = %s WHERE mnemonic = %s',[eptid,app])
        #conn.commit()
        #response = make_response(render_template('new_func.html',app=app,func=eptid),200)
    #else:
        #response = make_response('your not a sysop!!!', 401)
    #return response()

    
# 6b.
# POST .../<app>/key
#body = API key (of Satosa token, laten we nu even buiten beschouwing)
@app.route('/<appl>/<key>', methods=['POST'])
@oidc_auth.oidc_auth('default')
def post_key(appl,key):
# basic authentication = de credentials voor de <app>
#0. credentials horen bij de <app>, zo niet return 401
# credentials in the route ?
#        return make_response('no credentials',401)
#1. API key begint met huc:, zo niet return 400
    if not key.startswith('huc'):
        return make_response('unknown api key',400)
#2. API key is bekend voor deze <app>, zo niet return 401
    cur.execute('''SELECT u._id,u.user_info FROM invitation AS i
         JOIN application AS a ON a._id = i.app
         JOIN users AS u ON i.usr = u._id
         JOIN key AS k ON k.usr =u._id
            WHERE k.key = %s AND a.mnemonic = %s
''',[key,appl])
    res = cur.fetchall()
    if not res:
        return make_response('unknown api key',401)
#3. geef de user info voor de API key terug
    user_info = res[0][1]
    return make_response(f'user info: {user_info}',200)


@app.route('/<appl>', methods=['POST'])
@auth.login_required
def post_appl(appl):
    #TODO 20240304: check that <appl> = the logged in user
    if auth.current_user() != appl and auth.current_role()!= 'sysop':
        return make_response('unauthorized',401)
        pass
        #TODO 20240304: return unauthorized
    logging.debug(f'post_appl: {appl}')
    logging.debug(f'values: {request.values}')
    logging.debug(f'form: {request.form}')
    logging.debug(f'key: {request.form.get("key")}')

    key = request.values["key"]
    logging.debug(f'key: {key}')
#1. API key begint met huc:, zo niet return 400
    if  not key.startswith('huc'):
        return make_response('unknown api key',401)
#2. API key is bekend voor deze <app>, zo niet return 401
    cur.execute('''SELECT u._id,u.user_info FROM invitation AS i
         JOIN application AS a ON a._id = i.app
         JOIN users AS u ON i.usr = u._id
         JOIN key AS k ON k.usr =u._id
            WHERE k.key = %s AND a.mnemonic = %s
''',[key,appl])
    res = cur.fetchall()
    if not res:
        return make_response('unknown api key',401)
#3. geef de user info voor de API key terug
#    usr = res[0]['_id']
#    cur.execute("SELECT user_info FROM users WHERE _id = %s ",[usr])
    user_info = res[0][1]
    return jsonify(user_info)



def stderr(text,nl='\n'):
    sys.stderr.write(f'{text}{nl}')


letters = string.ascii_letters
digits = string.digits
special_chars = re.sub(r'["\'\\!]','',string.punctuation)
alphabet = letters + digits + special_chars

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

conn = None
cur = None
try:
    # read database configuration
    params = { 'host' : os.environ.get('DATABASE_HOST', 'localhost'),
                'port' : int(os.environ.get('DATABASE_PORT', 5432)),
                'database' : os.environ.get('DATABASE_DB', 'sleutelkastje'),
                'user' : os.environ.get('DATABASE_USER', 'test'),
                'password' : os.environ.get('DATABASE_PASSWORD', 'test') }
        
    logging.debug(params)
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)
    # create a new cursor
    cur = conn.cursor()
    #TODO 20240304: the apps, e.g., todo, should be loaded from the database and their <app>,<cred> added to the users dictionary
    # up till now: always None ???
    result = cur.execute("SELECT * FROM application")
    logging.debug(f'all appl-s: {result}')
    # add to users
except Exception as e:
    logging.debug(f'connection to db failed:\n{e}')


if __name__ == "__main__":
#    auth.init_app(app)
    app.run()


