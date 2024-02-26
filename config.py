import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(app_dir, "db/recipe_db.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_FOLDER = os.path.join(app_dir, 'static/avatars')
    ALLOWED_EXTENSIONS = {'png', 'jpg'}


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
