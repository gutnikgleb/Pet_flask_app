from var2 import db, current_date


class SitePages(db.Model):
    __tablename__ = 'site_pages'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(50), nullable=False)
    for_reg = db.Column(db.Boolean, default=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    psw = db.Column(db.String(500), nullable=False)
    ava = db.Column(db.String(500), default='default.png')
    date = db.Column(db.DateTime, default=current_date)


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    recipe = db.Column(db.Text, nullable=True)
    kkal = db.Column(db.Numeric(5, 2), nullable=True)
    prots = db.Column(db.Numeric(5, 2), nullable=True)
    fats = db.Column(db.Numeric(5, 2), nullable=True)
    carbs = db.Column(db.Numeric(5, 2), nullable=True)
    k_shrink = db.Column(db.Numeric(5, 2), nullable=True)
    public = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=current_date)
    final_weight = db.Column(db.Numeric(7, 2), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    kkal = db.Column(db.Numeric(5, 2))
    prots = db.Column(db.Numeric(5, 2))
    fats = db.Column(db.Numeric(5, 2))
    carbs = db.Column(db.Numeric(5, 2))


class RecipeHasProduct(db.Model):
    __tablename__ = 'recipe_has_product'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    weight = db.Column(db.Numeric(7, 2), nullable=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=current_date)
