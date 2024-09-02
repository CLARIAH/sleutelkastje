from sleutelkastje.application import db
import sqlalchemy as sa
import sqlalchemy.orm as orm


class Invitation(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    app_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('application.id'))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'), nullable=True)

    application: orm.Mapped['Application'] = orm.relationship(back_populates="invitations")
    user: orm.Mapped['User'] = orm.relationship(back_populates='invitations')

    def __repr__(self):
        return f'<Invitation {self.id}>'


class Key(db.Model):
    """
    This model represents an API key linked to a user.
    """
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    key: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('user.id'))

    user: orm.Mapped['User'] = orm.relationship(back_populates="keys")
