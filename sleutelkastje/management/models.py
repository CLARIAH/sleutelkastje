from typing import List

from sleutelkastje.application import db
import sqlalchemy as sa
import sqlalchemy.orm as orm


class Invitation(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    role: orm.Mapped[str]
    app_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('application.id'))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)

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
            'role': self.role
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

    def to_dict(self):
        """
        Converts the object to a dictionary.
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
        }
