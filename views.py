import os
from var2 import app, db, login_manager
from models import SitePages, Users, Recipes, Products, RecipeHasProduct, Comments
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    make_response
)
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin
)
from forms import (
    LoginForm,
    RegisterForm,
    ProfileUpdateForm,
    AddRecipeForm,
    AddProductForm,
    RecipeUpdateForm,
    CommentForm
)


def register_validator(username: str, email: str) -> bool:
    if str(username) == str(email):
        flash('Никнейм и email не должны совпадать', 'error')
        return False
    return True


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


class UserLogin(UserMixin):
    """Класс для описания состояния текущего пользователя"""

    def fromDB(self, user_id):
        self.__user = Users.query.filter_by(id=user_id).first()
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.id)

    def getName(self):
        return self.__user.username if self.__user else "Без ника"

    def getEmail(self):
        return self.__user.email if self.__user else "Без email"

    def updateInfo(self, column: str, value: str):
        try:
            exec(f"self.__user.{column} = {str(value)}")
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            flash(f"Ошибка добавления в БД для {column}", "error")
            print(f"Ошибка добавления в БД для {column}" + str(e))
            return False

    def getAvatar(self):
        img = None
        try:
            with app.open_resource(app.root_path + url_for('static', filename=f'avatars/{self.__user.ava}'), 'rb') as f:
                img = f.read()
        except FileNotFoundError as e:
            print("Не найден аватар по умолчанию: " + str(e))

        return img


@app.route("/")
def index():
    recipes = Recipes.query.filter_by(public=1).all()

    if current_user.is_authenticated:
        menu = SitePages.query.filter_by(for_reg=1).all()
    else:
        menu = SitePages.query.filter_by(for_reg=0).all()
    return render_template('index.html', menu=menu, recipes=recipes)


@app.errorhandler(404)
def PageNotFound(error):
    """Страница для неподготовленной ссылки"""
    if current_user.is_authenticated:
        menu = SitePages.query.filter_by(for_reg=1).all()
    else:
        menu = SitePages.query.filter_by(for_reg=0).all()
    return render_template('page404.html', title='Страница не найдена', menu=menu)


@app.route("/login", methods=('POST', 'GET'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.psw, form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(url_for('profile'))
        else:
            flash("Попробуйте снова, что-то введено не так", "error")

    menu = SitePages.query.filter_by(for_reg=0).all()
    return render_template('login.html', menu=menu, form=form, title='Авторизация')


@app.route('/register', methods=('POST', 'GET'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = RegisterForm()
    if form.validate_on_submit():
        if not register_validator(form.username.data, form.email.data):
            return redirect(url_for('register'))
        try:
            hashed_pass = generate_password_hash(form.psw1.data)
            new_user = Users(username=form.username.data, email=form.email.data, psw=hashed_pass)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Ошибка добавления в БД", "error")
            print("Ошибка добавления в БД " + str(e))

    menu = SitePages.query.filter_by(for_reg=0).all()
    return render_template('register.html', menu=menu, form=form, title='Регистрация')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    menu = SitePages.query.filter_by(for_reg=1).all()
    recipes = []
    try:
        recipes = Recipes.query.filter_by(user_id=current_user.get_id()).order_by(Recipes.date.desc()).all()
    except SQLAlchemyError as e:
        print(str(e))
    return render_template('profile.html', menu=menu, recipes=recipes)


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar()
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image.png'
    return h


@app.route('/profile_update', methods=('POST', 'GET'))
@login_required
def profile_update():
    form = ProfileUpdateForm()
    user_4update = Users.query.filter_by(id=current_user.get_id()).first()
    data_4update = []
    if form.validate_on_submit():
        try:
            if form.username.data and form.username.data != user_4update.username:
                user_4update.username = form.username.data
                data_4update.append('Никнейм')
            if form.psw1.data:
                user_4update.psw = generate_password_hash(form.psw1.data)
                data_4update.append('Пароль')
            if form.avatar.data:
                ava_name = form.avatar.data.filename
                ava = form.avatar.data
                avatar_folder = app.config['UPLOAD_FOLDER']
                path = os.path.join(avatar_folder, ava_name)
                ava.save(path)
                user_4update.ava = ava_name
                data_4update.append('Ава')

            if data_4update:
                db.session.commit()
            flash(f"{', '.join(data_4update) if data_4update else 'Данные'} были обновлены", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Ошибка добавления в БД", "error")
            print(f"Ошибка добавления в БД" + str(e))

    menu = SitePages.query.filter_by(for_reg=1).all()
    return render_template('profile_update.html', menu=menu, title="Изменение профиля", form=form)


@app.route('/new_recipe', methods=('POST', 'GET'))
@login_required
def new_recipe():
    form = AddRecipeForm()
    if form.validate_on_submit():
        try:
            recipe = Recipes(name=form.name.data,
                             recipe=form.recipe.data,
                             public=form.is_public.data,
                             user_id=current_user.get_id())
            db.session.add(recipe)
            db.session.commit()
            flash("Рецепт добавлен", "success")
            return redirect(url_for('new_recipe'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Ошибка добавления в БД", "error")
            print(f"Ошибка добавления рецепта в БД" + str(e))

    menu = SitePages.query.filter_by(for_reg=1).all()
    return render_template('add_recipe.html', menu=menu, title="Рецепт", form=form)


@app.route("/recipe/<int:id_recipe>", methods=('POST', 'GET'))
@login_required
def showRecipe(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    if int(current_user.get_id()) != recipe.user_id:
        if not recipe.public:
            return redirect(url_for('profile'))
        return redirect(url_for('showRecipe4Guest', id_recipe=id_recipe))

    products_4recipe = db.session.query(Products, RecipeHasProduct).join(
        RecipeHasProduct, Products.id == RecipeHasProduct.product_id).filter(
        RecipeHasProduct.recipe_id == recipe.id).all()

    comments = db.session.query(Users, Comments).join(Comments, Users.id == Comments.user_id).filter(
        Comments.recipe_id == id_recipe).order_by(Comments.date).all()

    form = CommentForm()
    if form.validate_on_submit():
        try:
            new_comment = Comments(user_id=current_user.get_id(), recipe_id=id_recipe, comment=form.comment.data)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('showRecipe', id_recipe=id_recipe))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка добавления комментария в БД" + str(e))

    menu = SitePages.query.filter_by(for_reg=1).all()
    return render_template('recipe.html',
                           menu=menu,
                           recipe=recipe,
                           products=products_4recipe,
                           comments=comments,
                           form=form)


@app.route("/guest/recipe/<int:id_recipe>", methods=('POST', 'GET'))
def showRecipe4Guest(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    products_4recipe = db.session.query(Products, RecipeHasProduct).join(
        RecipeHasProduct, Products.id == RecipeHasProduct.product_id).filter(
        RecipeHasProduct.recipe_id == recipe.id).all()

    comments = db.session.query(Users, Comments).join(Comments, Users.id == Comments.user_id).filter(
        Comments.recipe_id == id_recipe).order_by(Comments.date).all()

    form = CommentForm()
    if form.validate_on_submit():
        try:
            new_comment = Comments(user_id=current_user.get_id(), recipe_id=id_recipe, comment=form.comment.data)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('showRecipe', id_recipe=id_recipe))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка добавления комментария в БД" + str(e))

    if current_user.is_authenticated:
        menu = SitePages.query.filter_by(for_reg=1).all()
    else:
        menu = SitePages.query.filter_by(for_reg=0).all()
    return render_template('recipe_for_guest.html',
                           menu=menu,
                           recipe=recipe,
                           products=products_4recipe,
                           comments=comments,
                           form=form,
                           user_status=current_user.is_authenticated)


@app.route("/recipe/<int:id_recipe>/change_recipe", methods=('POST', 'GET'))
@login_required
def change_recipe(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    if int(current_user.get_id()) != recipe.user_id:
        return redirect(url_for('profile'))

    form = RecipeUpdateForm()
    if form.validate_on_submit():
        try:
            if form.name.data:
                recipe.name = form.name.data
            if form.recipe.data:
                recipe.recipe = form.recipe.data
            if form.final_weight.data:
                recipe.final_weight = form.final_weight.data
            recipe.public = form.is_public.data

            db.session.commit()
            return redirect(url_for("showRecipe", id_recipe=recipe.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Ошибка добавления в БД", "error")
            print(f"Ошибка добавления в БД" + str(e))

    menu = SitePages.query.filter_by(for_reg=1).all()
    return render_template('change_recipe.html', menu=menu, title="Изменение рецепта", form=form, recipe=recipe)


@app.route("/recipe/<int:id_recipe>/del_recipe")
@login_required
def del_recipe(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    if int(current_user.get_id()) != recipe.user_id:
        return redirect(url_for('profile'))

    return "Здесь можно будет удалить рецепт"


@app.route("/recipe/<int:id_recipe>/add_product", methods=('POST', 'GET'))
@login_required
def add_product(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    if int(current_user.get_id()) != recipe.user_id:
        return redirect(url_for('profile'))

    form = AddProductForm()
    if form.validate_on_submit():
        try:
            pr = Products(name=form.name.data,
                          kkal=form.kkal.data,
                          prots=form.prots.data,
                          fats=form.fats.data,
                          carbs=form.carbs.data)
            db.session.add(pr)
            db.session.flush()
            r_h_pr = RecipeHasProduct(recipe_id=recipe.id,
                                      product_id=pr.id,
                                      weight=form.weight.data)
            db.session.add(r_h_pr)
            db.session.commit()
            flash(f'Продукт добавлен в состав "{recipe.name}"', "success")
            return redirect(url_for('add_product', id_recipe=recipe.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Ошибка добавления в БД", "error")
            print(f"Ошибка добавления в БД" + str(e))

    menu = SitePages.query.filter_by(for_reg=1).all()
    return render_template('add_product.html', menu=menu, title="Добавить продукт", form=form, recipe=recipe)


@app.route("/recipe/<int:id_recipe>/calculate_macros")
@login_required
def calculate_macros(id_recipe):
    recipe = Recipes.query.filter_by(id=id_recipe).first()
    if int(current_user.get_id()) != recipe.user_id:
        return redirect(url_for('profile'))

    products_4recipe = db.session.query(Products, RecipeHasProduct).join(
        RecipeHasProduct, Products.id == RecipeHasProduct.product_id).filter(
        RecipeHasProduct.recipe_id == recipe.id).all()

    if not products_4recipe:
        flash("Список продуктов пуст", "error")
    if not recipe.final_weight:
        flash("Введите вес готового продукта", "error")

    total_products_weight = 0
    total_prot = 0
    total_fat = 0
    total_carbs = 0
    total_kkal = 0
    for pr, r_h_pr in products_4recipe:
        total_products_weight += r_h_pr.weight
        total_prot += (pr.prots * r_h_pr.weight / 100)
        total_fat += (pr.fats * r_h_pr.weight / 100)
        total_carbs += (pr.carbs * r_h_pr.weight / 100)
        total_kkal += ((pr.prots * r_h_pr.weight / 100 + pr.carbs * r_h_pr.weight / 100)
                       * 4 + pr.fats * r_h_pr.weight / 100 * 9)
    try:
        recipe.k_shrink = round(total_products_weight / recipe.final_weight, 2)
        f_w = recipe.final_weight / 100
        recipe.prots = round(total_prot / f_w, 2)
        recipe.fats = round(total_fat / f_w, 2)
        recipe.carbs = round(total_carbs / f_w, 2)
        recipe.kkal = round(total_kkal / f_w, 2)
        db.session.commit()

        return redirect(url_for('showRecipe', id_recipe=recipe.id))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Ошибка добавления в БД", "error")
        print(f"Ошибка добавления в БД" + str(e))
