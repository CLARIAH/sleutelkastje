from typing import List

from sqlalchemy import JSON

from sleutelkastje.application import db
import sqlalchemy.orm as orm


class User(db.Model):
    """
    This class represents a user in the database.

    When the password hash is None, this user can only sign in using OIDC or an API key.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(unique=True)
    user_info: orm.Mapped[JSON] = orm.mapped_column(type_=JSON)
    password_hash: orm.Mapped[str] = orm.mapped_column(nullable=True)

    invitations: orm.Mapped[List['Invitation']] = orm.relationship(back_populates="user")
    applications: orm.Mapped[List['Application']] = orm.relationship(back_populates="functional_admin")
    keys: orm.Mapped[List['Key']] = orm.relationship(back_populates='user')
