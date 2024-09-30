import logging

from flask import jsonify, make_response, request
from flask_login import current_user, login_required

from sleutelkastje.application import db
from sleutelkastje.authentication import auth, get_user_by_key, permission
from sleutelkastje.management import Invitation, Item, bp, get_invite, is_func, key_valid
from sleutelkastje.sysop import Application, ApplicationUserAssociation


def check_func(app: str):
    """
    Check if the current user is func admin of the app. app_arg is the name of the function arg
    of the wrapped function which contains the app. Must be a kwarg (Flask does this by default for
    any variables included from routes.
    :param app:
    :return:
    """
    return is_func(app, current_user.id)


def check_can_view(app: str):
    """
    Check if the current user can view this application.
    :param app:
    :return:
    """
    applications = current_user.applications
    for application in applications:
        if application.mnemonic == app:
            return True
    return False


@bp.route('/list', methods=["GET"])
@login_required
def index():
    """
    Retrieves all apps this user can manage.
    :return:
    """
    applications = current_user.application_associations

    return make_response(jsonify({
        'applications': [
            {
                'name': app.application.name,
                'mnemonic': app.application.mnemonic,
                'current_role': app.role
            } for app in applications
        ],
    }))


@bp.route('/<app>/details', methods=['GET'])
@login_required
@permission(check_can_view, 'app')
def app_details(app):
    """
    Get details of an application.
    :param app:
    :return:
    """
    application = db.session.query(Application).filter_by(mnemonic=app).first()

    return make_response(jsonify({
        'application': {
            'name': application.name,
            'mnemonic': application.mnemonic,
        }
    }))


@bp.route('/<app>/invitations', methods=['GET'])
@login_required
@permission(check_func, 'app')
def get_invites(app):
    """
    Get the invites for an application.
    :param app:
    :return:
    """
    application = db.session.query(Application).filter_by(mnemonic=app).first()
    invitations = application.invitations
    return make_response(jsonify({
        "invites": [invitation.to_dict() for invitation in invitations]
    }))


@bp.route('/<app>/invitations', methods=['DELETE'])
@login_required
@permission(check_func, 'app')
def delete_invitations(app):
    """
    Bulk delete invitations by their ID
    :param app:
    :return:
    """
    application = db.session.query(Application).filter_by(mnemonic=app).first()
    body = request.get_json()

    if 'ids' not in body:
        return jsonify({'success': False, 'error': 'No IDs provided'}), 400

    ids = body['ids']

    invitations = db.session.query(Invitation).filter(Invitation.id.in_(ids), Invitation.app_id == application.id).all()
    for invitation in invitations:
        db.session.delete(invitation)
    db.session.commit()

    return jsonify({'success': True}), 200


@bp.route('/<app>/invitations', methods=['POST'])
@login_required
@permission(check_func, 'app')
def invite(app):
    """
    Invite a user for the application.
    :param app:
    :return:
    """
    body = request.get_json()

    if 'role' not in body:
        return jsonify({'success': False, 'error': 'No role provided'}), 400

    role = body['role']

    uuid = get_invite()
    logging.debug(f'app[{app}] invite[{uuid}]')
    application = db.session.query(Application).filter_by(mnemonic=app).first()

    invitation = Invitation(
        uuid=uuid,
        application=application,
        role=role
    )

    db.session.add(invitation)
    db.session.commit()

    return jsonify({
        "application": application.mnemonic,
        "inviteId": invitation.uuid
    }), 201


@bp.route('/invitations/<invitation_id>', methods=['GET'])
@login_required
def get_invitations(invitation_id: str):
    """
    Get invitation details
    :param invitation_id:
    :return:
    """
    invitation = db.session.query(Invitation).filter_by(uuid=invitation_id).first_or_404()
    if invitation.user_id is not None:
        return jsonify({
            "error": "Invitation used"
        }), 200

    return jsonify({
        "code": invitation_id,
        "appName": invitation.application.name,
        "appId": invitation.application.mnemonic,
        "role": invitation.role
    })


@bp.route('/invitations/<invitation_id>', methods=['POST'])
@login_required
def register(invitation_id: str):
    """
    User registers by accepting an invitation.
    :param invitation_id:
    :return:
    """
    body = request.get_json()
    action = body.get('action', '')
    if action not in ['accept', 'reject']:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400

    invitation = db.session.query(Invitation).filter_by(uuid=invitation_id).first_or_404()
    if invitation.user_id is not None:
        return jsonify({
            "error": "Invitation used"
        }), 400

    if action == 'accept':
        invitation.user = current_user
        invitation.application.user_associations.append(ApplicationUserAssociation(
            user=current_user,
            role=invitation.role
        ))

        db.session.commit()

        eppn = current_user.username
        application = invitation.application
        # check result
        appl = application.mnemonic
        return jsonify({
            "success": True,
        }), 200
    if action == 'reject':
        db.session.delete(invitation)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Invitation rejected"
        }), 200


@bp.route('/<appl>/validate', methods=['POST'])
@login_required
@permission(check_func, 'appl')
def post_appl(appl: str):
    key = request.values["key"]
    logging.debug(f'key: {key}')

    application = db.session.query(Application).filter_by(mnemonic=appl).first()

    user = get_user_by_key(key)

    if user is None:
        return jsonify({
            'status': 'unauthorized',
            'message': 'submitted API key is not known',
        }), 200

    for app_assoc in user.application_associations:
        if app_assoc.app_id == application.id:
            return jsonify({
                "status": "success",
                "userData": {
                    "username": user.username,
                    "nickname": user.nickname,
                    "role": app_assoc.role
                }
            })

    return jsonify({
        'status': 'unauthorized',
        'message': 'submitted API key is not known',
    }), 200


@bp.route('/<app>/items', methods=['GET'])
@login_required
@permission(check_func, 'app')
def get_items(app: str):
    """
    Get all items of this app
    :param app:
    :return:
    """
    application = db.session.query(Application).filter_by(mnemonic=app).first_or_404()
    items = application.items
    return jsonify({
        "items": [item.to_dict() for item in items]
    }), 200


@bp.route('/<app>/items', methods=['POST'])
@login_required
@permission(check_func, 'app')
def create_item(app: str):
    """
    Create a new item
    :param app:
    :return:
    """
    application = db.session.query(Application).filter_by(mnemonic=app).first_or_404()
    body = request.get_json()
    if 'name' not in body:
        return jsonify({'success': False, 'error': 'No item name provided'}), 400

    name = body['name']
    item = db.session.query(Item).filter_by(name=name, app_id=application.id).first()
    if item is not None:
        return jsonify({'success': False, 'error': 'Item already exists'}), 400

    item = Item(name=name, application=application)
    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Item created', 'item': item.to_dict()}), 201
