from flask import jsonify, make_response, redirect, request, session
from flask_login import current_user, login_required, login_user, logout_user
from flask_pyoidc.user_session import UserSession

from sleutelkastje import app
from sleutelkastje.application import db
from sleutelkastje.authentication import User, bp, oidc_auth, verify_password
from sleutelkastje.authentication.authentication import get_api_key, hash_password, load_user
from sleutelkastje.authentication.models import Key
from sleutelkastje.sysop import Application, ApplicationUserAssociation


@bp.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    """
    Get user info, check if logged in
    :return:
    """
    return jsonify({
        'username': current_user.username,
        'nickname': current_user.nickname,
        'role': current_user.role,
        'profileComplete': current_user.profile_complete,
        'isOidc': current_user.is_oidc,
    })


@bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Log in the user
    :return:
    """
    data = request.json

    username = data['username']
    password = data['password']

    username_verified = verify_password(username, password)

    if username_verified is None:
        # Unauthorized
        return make_response(jsonify({
            'error': 'Invalid username or password',
        }), 403)

    user = db.session.query(User).filter_by(username=username).first()

    login_user(user)

    return jsonify({
        "message": "Login successful"
    }), 200


@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the user.
    :return:
    """
    logout_user()
    return jsonify({
        "message": "Logout successful"
    }), 200


@bp.route('/api/auth/complete-profile', methods=['POST'])
@login_required
def complete_profile():
    """
    Complete user profile
    :return:
    """
    if current_user.profile_complete:
        return jsonify({
            'message': 'User profile already complete'
        }), 403

    data = request.json

    current_user.profile_complete = True
    current_user.nickname = data['nickname']
    db.session.commit()
    return jsonify({
        'message': 'Profile completed'
    }), 200


@bp.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change the user password
    :return:
    """
    if current_user.is_oidc:
        return jsonify({
            "status": "error",
            "message": "You have an OIDC account. You cannot change your password in here, change it in the OIDC "
                       "settings"
        }), 403

    data = request.json
    if not all(x in data for x in ['oldPassword', 'newPassword']):
        return jsonify({
            "status": "error",
            "message": "Incorrect arguments. Please make sure your body contains 'oldPassword' and 'newPassword'."
        }), 400

    if not verify_password(current_user.username, data['oldPassword']):
        return jsonify({
            "status": "error",
            "message": "Incorrect old password"
        }), 403

    current_user.password_hash = hash_password(data['newPassword'])
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Password changed"
    }), 200


@bp.route('/api/keys', methods=['GET'])
@login_required
def get_api_keys():
    """
    Get API keys for this user
    :return:
    """
    keys = current_user.keys
    return jsonify({
        "keys": [{
            "name": key.name,
            "application": key.application.name if key.application is not None else 'Sleutelkastje',
            "readable_part": f"huc:{key.key_prefix}",
            "last_used": key.last_used,
        } for key in keys]
    }), 200


@bp.route('/api/keys', methods=['POST'])
@login_required
def generate_api_key():
    """
    Generate a new API key for this user.
    :return:
    """
    data = request.json
    key_name = data['name']
    application_mnemonic = data.get('appMnemonic', None)

    prefix, key_raw = get_api_key()
    key = Key(
        name=key_name,
        key_hash=hash_password(key_raw),
        key_prefix=prefix,
        user=current_user,
    )

    if application_mnemonic not in [None, '']:
        # Validate if the user has access to the application
        application = db.session.query(Application).filter_by(mnemonic=application_mnemonic).first()
        if application is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid application'
            }), 400
        application_association = (db.session.query(ApplicationUserAssociation)
                                   .filter_by(app_id=application.id, user_id=current_user.id)).one_or_none()
        if application_association is None:
            return jsonify({
                'status': 'error',
                'message': 'Cannot create key for an application you cannot access'
            }), 403
        key.application_id = application.id

    db.session.add(key)
    db.session.commit()
    return jsonify({
        'name': key_name,
        'key': key_raw
    }), 201


@bp.route('/api/keys/bulk-delete', methods=['POST'])
@login_required
def delete_api_keys():
    """
    Delete API keys for this user.
    :return:
    """
    body = request.get_json()

    if 'prefixes' not in body:
        return jsonify({'success': False, 'error': 'No prefixes provided'}), 400

    prefixes = body['prefixes']

    keys = db.session.query(Key).filter(Key.user==current_user, Key.key_prefix.in_(prefixes)).all()
    for key in keys:
        db.session.delete(key)
    db.session.commit()

    return jsonify({'success': True}), 200


@bp.route('/oidc/login')
@oidc_auth.oidc_auth('default')
def oidc_login():
    user_session = UserSession(session)
    userinfo = user_session.userinfo
    eppn = userinfo['eppn'][0]

    user = load_user(eppn)
    if user is None:
        user = User(
            username=eppn,
            user_info=userinfo,
            is_oidc=True,
            nickname=userinfo.get('nickname', ''),
        )
        db.session.add(user)
        db.session.commit()
    elif user.user_info is {} or user.is_oidc is False:
        user.user_info = userinfo
        user.nickname = userinfo.get('nickname', '')
        user.is_oidc = True
        db.session.add(user)
        db.session.commit()

    login_user(user)

    redirect_target = request.args.get('next')

    frontend_base = app.config['FRONTEND_HOST']
    return redirect(f"{frontend_base}{redirect_target}", code=302)
