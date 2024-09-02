from typing import List

from sleutelkastje.application import db
import sqlalchemy as sa
import sqlalchemy.orm as orm


class Application(db.Model):
    """
    An application for which authentication is managed using the Sleutelkastje.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    mnemonic: orm.Mapped[str] = orm.mapped_column(sa.String, unique=True, index=True)
    credentials: orm.Mapped[str] = orm.mapped_column(sa.String)
    redirect: orm.Mapped[str] = orm.mapped_column(sa.String)
    functional_admin_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)

    invitations: orm.WriteOnlyMapped[List['Invitation']] = orm.relationship(back_populates="application")

    functional_admin: orm.Mapped['User'] = orm.relationship(back_populates="applications")

    def __repr__(self):
        return f'<Application {self.mnemonic}>'
