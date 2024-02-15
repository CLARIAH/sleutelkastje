# -*- coding: utf-8 -*-
import datetime
import flask
from flask import Flask, Response, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
import json
import logging
import os
import psycopg2
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
    "sysop": generate_password_hash("striktgeheim"),
    "todo" : generate_password_hash("ookgeheim")
}
#TODO: the apps, e.g., todo, should be loaded from the database

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route("/hello")
@auth.login_required
def hello_world():
    return "Hello, {}!".format(auth.current_user())


# 1. register app
@app.route('/add/appl=<app>,cred=<cred>,redir=<url>', methods=['POST'])
@auth.login_required
def add_app(app,cred,url):
    #TODO: check that logged in user is sysop
    logging.debug(f'add app[{app}] - cred[{cred}] - url[{url}]')
    # add app to database
    cur.execute('INSERT INTO application(mnemonic, credentials, redirect) VALUES (%s, %s, %s)',
            (app,cred,url))
    conn.commit()
    return make_response(render_template('succes.html',result=app),200)


@app.route('/find/<app>', methods=['GET'])
def get_app(app):
    logging.debug(f'get app[{app}]')
    result = cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    response = make_response(render_template('get.html',result=result),200)
    return response

# 3. user invited 
@app.route('/invite/<app>/<invite>', methods=['GET'])
@oidc_auth.oidc_auth('default')
def invite(app,invite):
    logging.debug(f'app[{app}] invite[{invite}]')
    cur.execute("SELECT _id FROM application WHERE mnemonic = %s",[app])
    app_id = cur.fetchone()
    cur.execute('INSERT INTO invitation(uuid, app) VALUES (%s, %s)',
            (invite, app_id))
    conn.commit()
    response = make_response(render_template('invite.html',invite=invite,app=app),200)
    return response

def get_api_key():
    api_key = 'huc:'
    for i in range(16):
        api_key += ''.join(secrets.choice(alphabet))
    return api_key

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
    inv_id,uuid,appl,usr_id = cur.fetchone()
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
    response = make_response(render_template('accepted.html',person=uuid,app=appl,key=api_key),200)
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
@auth.login_required
def add_func_eppn(app,eppn):
    #TODO: check that logged in user is sysop
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
@app.route('/<app>/func,eptid=<eptid>', methods=['POST'])
@auth.login_required
def add_func_eptid(app,eptid):
    #TODO: check that logged in user is sysop
    logging.debug(f'add functioneel beheerder eptid[{eptid}] to app[{app}]')
    cur.execute('UPDATE application SET funcPerson = %s WHERE mnemonic = %s',[eptid,app])
    conn.commit()
    response = make_response(render_template('new_func.html',app=app,func=eptid),200)
    return response

    
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
    #TODO: check that appl = the logged in user
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
except Exception as e:
    logging.debug(f'connection to db failed:\n{e}')


if __name__ == "__main__":
#    auth.init_app(app)
    app.run()


