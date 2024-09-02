from sleutelkastje.application import app

from sleutelkastje.authentication import bp as authentication_bp
import sleutelkastje.database
from sleutelkastje.sysop import bp as sysop_bp
from sleutelkastje.management import bp as management_bp

app.register_blueprint(authentication_bp)
app.register_blueprint(sysop_bp)
app.register_blueprint(management_bp)
