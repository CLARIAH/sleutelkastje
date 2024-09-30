from flask_login import current_user, login_required

from sleutelkastje import app
from sleutelkastje.management import Invitation, get_invite
from sleutelkastje.sysop import Application, ApplicationUserAssociation, bp
from sleutelkastje.application import db
from sleutelkastje.authentication import User, hash_password, permission

import logging

from flask import jsonify, request, make_response, render_template


def is_sysop():
    """
    Permission check for sysop
    :return:
    """
    return current_user.role == 'sysop'


@bp.route('/apps/<application>', methods=['PUT'])
@login_required
@permission(is_sysop)
def add_app(application):
    """
    Create a new application.
    :param application:
    :return:
    """
    body = request.get_json()
    cred = body['credentials']
    url = body['redirect']
    name = body['name']
    logging.debug(f'add app[{application}] - cred[{cred}] - url[{url}]')
    app_object = db.session.query(Application).filter_by(mnemonic=application).first()

    status: str
    if app_object is None:
        app_object = Application(
            mnemonic=application,
            credentials=hash_password(cred),
            name=name,
            redirect=url,
        )
        db.session.add(app_object)
        status, code = 'created', 201
        user = User(
            username=application,
            password_hash=hash_password(cred),
            user_info={}
        )
        db.session.add(user)
    else:
        app_object.credentials = hash_password(cred)
        app_object.redirect = url
        app_object.name = name
        status, code = 'updated', 200

    db.session.commit()

    accept = request.headers.get('Accept', 'text/html')

    if accept == 'application/json':
        body = {
            'status': status,
            'message': f'Application {status}',
            'application': application
        }
        if status == 'created':
            invite = Invitation(
                uuid=get_invite(),
                application=app_object,
                role='operator',
            )
            db.session.add(invite)
            db.session.commit()
            frontend_base = app.config['FRONTEND_HOST']
            body['invitation'] = f"{frontend_base}/invitations/{invite.uuid}"
        return make_response(jsonify(body), code)
    return make_response(render_template('succes.html', result=application), code)


@bp.route('/apps/<appl>', methods=['GET'])
@login_required
@permission(is_sysop)
def get_app(appl):
    logging.debug(f'get app[{appl}]')
    # result = cur.execute("SELECT _id FROM application WHERE mnemonic = %s", [app])
    application = db.session.query(Application).filter_by(mnemonic=appl).first_or_404()
    response = make_response(render_template('get.html', application=application), 200)
    return response


@bp.route('/apps/<appl>/func', methods=['POST'])
@login_required
@permission(is_sysop)
def add_func_eppn(appl: str):
    """
    Create a functional admin for the application

    Expects a JSON body with an 'eppn' key
    :param appl: The name of the application
    :return:
    """
    body = request.get_json()
    eppn: str = body['eppn']
    logging.debug(f'add functioneel beheerder eppn[{eppn}] to app[{appl}]')

    application = db.session.query(Application).filter_by(mnemonic=appl).first_or_404()
    user = db.session.query(User).filter_by(username=eppn).first()

    if user is None:
        user = User(username=eppn, user_info={})
        db.session.add(user)

    application.user_associations.append(ApplicationUserAssociation(
        user=user,
        role='operator',
    ))
    db.session.commit()

    accept = request.headers.get('Accept', 'text/html')
    if accept == 'application/json':
        return make_response(jsonify({
            'status': 'ok',
            'message': 'Functional admin added',
            'application': appl,
            'operator': user.username,
        }), 200)
    response = make_response(render_template('new_func.html', app=appl, func=eppn), 200)
    return response
