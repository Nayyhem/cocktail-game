import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET', 'change_me_to_a_random_secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
