# import os
# basedir = os.path.abspath(os.path.dirname(__file__))


# class Config(object):
#     DEBUG = False
#     TESTING = False
#     CSRF_ENABLED = True
#     SECRET_KEY = 'this-really-needs-to-be-changed'
#     SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


# class ProductionConfig(Config):
#     DEBUG = False


# class StagingConfig(Config):
#     DEVELOPMENT = True
#     DEBUG = True


# class DevelopmentConfig(Config):
#     DEVELOPMENT = True
#     DEBUG = True


# class TestingConfig(Config):
#     TESTING = True
    
class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///dev1_db.sqlite3'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///prod1_db.sqlite3'



# class DevelopmentConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:fj3770ty@localhost:5432/Section3DB_dev'


# class ProductionConfig(Config):
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:fj3770ty@localhost:5432/Section3DB_prod'

