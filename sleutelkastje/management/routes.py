import logging

from flask import jsonify, make_response, render_template, request, session
from flask_pyoidc.user_session import UserSession

from sleutelkastje.application import db
from sleutelkastje.authentication import User, auth, get_api_key, hash_password, oidc_auth
from sleutelkastje.management import Invitation, Key, bp, get_invite, is_func, key_valid
from sleutelkastje.sysop import Application


@bp.route('/<app>/invite', methods=['GET'])
@oidc_auth.oidc_auth('default')
def invite(app):
    """
    Invite a user for the application.
    :param app:
    :return:
    """
    user_session = UserSession(session)
    userinfo = user_session.userinfo
    if not is_func(app, userinfo['eppn'][0]):
        return make_response('unauthorized', 401)
    uuid = get_invite()
    logging.debug(f'app[{app}] invite[{uuid}]')
    application = db.session.query(Application).filter_by(mnemonic=app).first()

    invitation = Invitation(
        uuid=uuid,
        application=application,
    )

    db.session.add(invitation)
    db.session.commit()

    response = make_response(render_template('invite.html', invite=uuid, app=app), 200)
    return response


@bp.route('/register/<invite_id>', methods=['GET'])
@oidc_auth.oidc_auth('default')
def register(invite_id: str):
    """
    User registers by accepting an invitation.
    :param invite_id:
    :return:
    """
    logging.debug(f'register invite[{invite_id}]')
    user_session = UserSession(session)
    userinfo = user_session.userinfo

    invite = db.session.query(Invitation).filter_by(uuid=invite_id).first_or_404()
    if invite.user_id is not None:
        response = make_response(render_template('invitation_used.html'), 200)
        return response

    user = db.session.query(User).filter_by(username=userinfo['eppn'][0]).first()
    if user is None:
        user = User(
            user_info=userinfo,
            username=userinfo['eppn'],
        )
        db.session.add(user)
    else:
        # Update user data, now that we have an up-to-date response from Satosa
        user.user_info = userinfo

    db.session.commit()

    logging.debug(f'new user_id: {user.id}')

    invite.user = user
    db.session.commit()

    key_plain = get_api_key()

    key = Key(
        key=key_plain,
        user=user
    )

    db.session.add(key)
    db.session.commit()

    eppn = userinfo['eppn'][0]
    application = invite.application
    # check result
    appl = application.mnemonic
    response = make_response(render_template('accepted.html', person=eppn, app=appl, key=key_plain), 200)
    return response


@bp.route('/<appl>/validate', methods=['POST'])
@auth.login_required
def post_appl(appl: str):
    if auth.current_user() != appl and auth.current_role() != 'sysop':
        logging.debug(f'error: unauthorized - status: 401')
        return make_response(jsonify({
            'status': 'error',
            'message': 'you are not allowed to validate API keys for this application',
        }), 403)

    key = request.values["key"]
    logging.debug(f'key: {key}')

    api_key, valid = key_valid(key, appl)

    if not valid:
        return make_response(
            jsonify({
                'status': 'unauthorized',
                'message': 'submitted API key is not known',
            }),
            401
        )

    user_info = api_key.user.user_info
    return jsonify(user_info)
