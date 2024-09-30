import logging
from flask import Flask
from flask_migrate import Migrate
from flask_seeder import FlaskSeeder
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sleutelkastje.application import Config

app = Flask(__name__, static_folder='frontend')


app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

seeder = FlaskSeeder()
seeder.init_app(app, db)

app.app_context().push()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

cors_origins = [app.config['FRONTEND_HOST']]

CORS(app, supports_credentials=True, resources={r'/*': {'origins': cors_origins}})
