import os
from dotenv import load_dotenv

load_dotenv()  # Load env vars

SECRET_KEY = os.getenv('SECRET_KEY')
SOURCE_DATA = os.getenv('SOURCE_DATA')

if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set in environment variables")

class Config:
    SECRET_KEY = SECRET_KEY
    SOURCE_DATA = SOURCE_DATA
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_app_password'
