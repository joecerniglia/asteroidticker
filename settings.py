import os
from flask_qa import create_app

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL).replace('postgres://', 'postgresql://')
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False
