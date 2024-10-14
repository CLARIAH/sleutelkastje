from flask_seeder import Seeder

from sleutelkastje.authentication import User
from sleutelkastje.authentication.authentication import hash_password, load_user


class SysopSeeder(Seeder):
    """
    Creates the sysop user
    """
    def run(self):
        sysop_user = load_user('sysop')
        if sysop_user is None:
            sysop_user = User(
                username='sysop',
                nickname='System Administrator',
                role='sysop',
                user_info={},
                password_hash=hash_password("change-me-please"),
                profile_complete=True,
                is_oidc=False
            )
            self.db.session.add(sysop_user)
            self.db.session.commit()
