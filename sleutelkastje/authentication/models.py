from datetime import datetime
from typing import List


from sleutelkastje.application import db
import sqlalchemy.orm as orm
import sqlalchemy as sa


class User(db.Model):
    """
    This class represents a user in the database.

    When the password hash is None, this user can only sign in using OIDC or an API key.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(unique=True)
    nickname: orm.Mapped[str] = orm.mapped_column(nullable=True)
    user_info: orm.Mapped[sa.JSON] = orm.mapped_column(type_=sa.JSON)
    password_hash: orm.Mapped[str] = orm.mapped_column(nullable=True)
    role: orm.Mapped[str] = orm.mapped_column(default='user')
    profile_complete: orm.Mapped[bool] = orm.mapped_column(server_default='0')
    is_oidc: orm.Mapped[bool] = orm.mapped_column(server_default='0')

    invitations: orm.Mapped[List['Invitation']] = orm.relationship(back_populates="user")

    applications: orm.Mapped[List['Application']] = orm.relationship(secondary="application_user_association", back_populates="users")
    application_associations: orm.Mapped[List['ApplicationUserAssociation']] = orm.relationship(back_populates="user")

    keys: orm.Mapped[List['Key']] = orm.relationship(back_populates='user')
    items: orm.Mapped[List['Item']] = orm.relationship(secondary='user_item_association', back_populates='users')
    item_associations: orm.Mapped[List['UserItemAssociation']] = orm.relationship(back_populates="user")

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self):
        """
        Get the unique identifier of the user.
        This is not the 'id', as that is only used as an internal database key. Instead, it is
        the 'username' which stores the unique identifier of the user.
        :return:
        """
        return self.username

    def to_dict(self):
        """
        Create a dict with the content of this model, for json serialization.
        :return:
        """
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
        }

    def __eq__(self, other):
        """
        Compare if two users are equal.
        :param other:
        :return:
        """
        return self.get_id() == other.get_id()


class Key(db.Model):
    """
    This model represents an API key linked to a user.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(default=datetime.now)
    name: orm.Mapped[str]
    key_hash: orm.Mapped[str] = orm.mapped_column(unique=True)
    key_prefix: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'))
    last_used: orm.Mapped[datetime] = orm.mapped_column(nullable=True)

    user: orm.Mapped['User'] = orm.relationship(back_populates="keys")
