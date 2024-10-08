import datetime
import os
import uuid


class Config:
    """
    Application configuration
    """
    FRONTEND_HOST = os.environ.get('FRONTEND_HOST', '')
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.environ.get('DATABASE_PORT', 5432)
    DATABASE_DB = os.environ.get('DATABASE_DB', 'sleutelkastje')
    DATABASE_USER = os.environ.get('DATABASE_USER', 'test')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'test')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}'
    OIDC_REDIRECT_URI = os.environ.get('APP_DOMAIN', 'http://localhost') + '/oidc/redirect'
    SECRET_KEY = os.environ.get('SECRET_KEY', uuid.uuid4().hex)
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=7)
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True
