import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = os.getenv('DB_PORT', '3306')
    DATABASE = os.getenv('DB_DATABASE', 'default_db')
    USERNAME = os.getenv('DB_USER', 'user')
    PASSWORD = os.getenv('DB_PASSWORD', 'password')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True