from typing import List

from sleutelkastje.application import db
import sqlalchemy as sa
import sqlalchemy.orm as orm

from sleutelkastje.authentication import User


class Invitation(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    role: orm.Mapped[str]
    app_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('application.id'))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    item_role_configuration: orm.Mapped[sa.JSON] = orm.mapped_column(type_=sa.JSON, server_default=sa.text("'{}'::json"))

    application: orm.Mapped['Application'] = orm.relationship(back_populates="invitations")
    user: orm.Mapped['User'] = orm.relationship(back_populates='invitations')

    def __repr__(self):
        return f'<Invitation {self.id}>'

    def to_dict(self):
        """
        Converts the object to a dictionary.
        :return:
        """
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user is not None else None,
            'role': self.role,
            'appId': self.application.mnemonic,
            'appName': self.application.name,
            'itemRoles': self.item_role_configuration,
            'code': self.uuid,
        }


class UserItemAssociation(db.Model):
    item_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('item.id'), primary_key=True)
    user_id: orm.Mapped[str] = orm.mapped_column(sa.ForeignKey('user.id'), primary_key=True)
    role: orm.Mapped[str]

    item: orm.Mapped["Item"] = orm.relationship(back_populates="user_associations")
    user: orm.Mapped["User"] = orm.relationship(back_populates="item_associations")


class Item(db.Model):
    """
    This model represents an Item, which is a part of an application to which a user can have access.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    app_id: orm.Mapped[str] = orm.mapped_column(sa.ForeignKey('application.id'))

    application: orm.Mapped['Application'] = orm.relationship(back_populates="items")
    users: orm.Mapped[List['User']] = orm.relationship(secondary="user_item_association", back_populates='items')
    user_associations: orm.Mapped[List['UserItemAssociation']] = orm.relationship(back_populates="item")

    def add_user(self, user: User, role: str) -> None:
        """
        Add a user to an item.
        :param user:
        :param role:
        :return:
        """
        if user in self.users:
            assoc = next(x for x in self.user_associations if x.user == user)
            assoc.role = role
        else:
            self.user_associations.append(UserItemAssociation(user_id=user.id, role=role))

    def to_dict(self):
        """
        Converts the object to a dictionary.
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
        }
