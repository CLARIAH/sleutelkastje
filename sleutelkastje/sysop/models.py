from typing import List

from sleutelkastje.application import db
import sqlalchemy as sa
import sqlalchemy.orm as orm

from sleutelkastje.authentication import User


class ApplicationUserAssociation(db.Model):
    app_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('application.id'), primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), primary_key=True)
    role: orm.Mapped[str]

    application: orm.Mapped['Application'] = orm.relationship(back_populates="user_associations")
    user: orm.Mapped['User'] = orm.relationship(back_populates="application_associations")


class Application(db.Model):
    """
    An application for which authentication is managed using the Sleutelkastje.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    mnemonic: orm.Mapped[str] = orm.mapped_column(sa.String, unique=True, index=True)
    name: orm.Mapped[str]
    credentials: orm.Mapped[str] = orm.mapped_column(sa.String)
    redirect: orm.Mapped[str] = orm.mapped_column(sa.String)
    functional_admin_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)

    invitations: orm.Mapped[List['Invitation']] = orm.relationship(back_populates="application")
    items: orm.Mapped[List['Item']] = orm.relationship(back_populates="application")

    functional_admin: orm.Mapped['User'] = orm.relationship()
    users: orm.Mapped[List['User']] = orm.relationship(secondary="application_user_association", back_populates="applications")
    user_associations: orm.Mapped[List[ApplicationUserAssociation]] = orm.relationship(back_populates="application")

    def __repr__(self):
        return f'<Application {self.mnemonic}>'

    def add_user(self, user: User, role: str) -> None:
        """
        Add a user to the application.
        :param user:
        :param role:
        :return:
        """
        if user in self.users:
            assoc = next(x for x in self.user_associations if x.user == user)
            assoc.role = role
        else:
            self.user_associations.append(ApplicationUserAssociation(user_id=user.id, role=role))
