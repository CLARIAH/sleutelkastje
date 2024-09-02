from sleutelkastje.sysop import Application, bp
from sleutelkastje.application import db
from sleutelkastje.authentication import User, hash_password, auth
from sleutelkastje.database import users

import logging

from flask import jsonify, request, make_response, render_template


@bp.route('/<application>', methods=['PUT'])
@auth.login_required(role='sysop')
def add_app(application):
    """
    Create a new application.
    :param application:
    :return:
    """
    body = request.get_json()
    cred = body['credentials']
    url = body['redirect']
    logging.debug(f'add app[{application}] - cred[{cred}] - url[{url}]')
    app = db.session.query(Application).filter_by(mnemonic=application).first()

    status: str
    if app is None:
        app = Application(
            mnemonic=application,
            credentials=hash_password(cred),
            redirect=url,
        )
        db.session.add(app)
        status, code = 'created', 201
    else:
        app.credentials = hash_password(cred)
        app.redirect = url
        status, code = 'updated', 200
    db.session.commit()
    users[application] = {"password": hash_password(cred), "role": "funcbeh"}

    accept = request.headers.get('Accept', 'text/html')

    if accept == 'application/json':
        return make_response(jsonify({
            'status': status,
            'message': 'Application added',
            'application': application
        }), code)
    return make_response(render_template('succes.html', result=application), code)


@bp.route('/find/<app>', methods=['GET'])
@auth.login_required(role='sysop')
def get_app(app):
    logging.debug(f'get app[{app}]')
    # result = cur.execute("SELECT _id FROM application WHERE mnemonic = %s", [app])
    application = db.session.query(Application).filter_by(mnemonic=app).first_or_404()
    response = make_response(render_template('get.html', application=application), 200)
    return response


@bp.route('/<app>/func', methods=['POST'])
@auth.login_required(role='sysop')
def add_func_eppn(app: str):
    """
    Create a functional admin for the application

    Expects a JSON body with an 'eppn' key
    :param app: The name of the application
    :return:
    """
    body = request.get_json()
    eppn: str = body['eppn']
    logging.debug(f'add functioneel beheerder eppn[{eppn}] to app[{app}]')

    application = db.session.query(Application).filter_by(mnemonic=app).first_or_404()
    user = db.session.query(User).filter_by(username=eppn).first()

    if user is None:
        user = User(username=eppn, user_info={})
        db.session.add(user)

    application.functional_admin = user
    db.session.commit()

    accept = request.headers.get('Accept', 'text/html')
    if accept == 'application/json':
        return make_response(jsonify({
            'status': 'ok',
            'message': 'Functional admin added',
            'application': app,
            'functional_admin': user.username,
        }), 200)
    response = make_response(render_template('new_func.html', app=app, func=eppn), 200)
    return response
