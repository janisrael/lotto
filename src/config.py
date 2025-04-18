import os
from dotenv import load_dotenv
from flask_mail import Mail

# Load .env variables
load_dotenv()

# Instantiate Flask-Mail
mail = Mail()

# Environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
SOURCE_DATA = os.getenv('SOURCE_DATA')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # App Password
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in environment variables")

# Main app configuration class
class Config:
    SECRET_KEY = SECRET_KEY
    SOURCE_DATA = SOURCE_DATA
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail config
    MAIL_SERVER = MAIL_SERVER
    MAIL_PORT = MAIL_PORT
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = MAIL_DEFAULT_SENDER
