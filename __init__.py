import os
import config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from forms import (
    LoginForm,
    RegisterForm,
    ProfileUpdateForm,
    AddRecipeForm,
    AddProductForm,
    RecipeUpdateForm,
    CommentForm
)

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
# перенаправление неавторизованного пользователя с недоступных страниц на страницу авторизации
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'


def current_date() -> datetime:
    time = datetime.now()
    time = time.replace(microsecond=0)
    return time


from views import *
