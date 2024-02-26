from flask_wtf import FlaskForm
from wtforms import (
    validators,
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    FloatField,
    FileField,
    SelectMultipleField
)
from wtforms.validators import DataRequired, input_required, Length, NumberRange, Optional, Email, EqualTo


def is_float(form, field):
    try:
        float(field.data)
    except ValueError:
        raise validators.ValidationError('Введите числовое значение')


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired('Обязательное поле'),
                                               Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired('Обязательное поле'),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Никнейм: ", validators=[DataRequired("Обязательное поле"),
                                                    Length(min=3, max=100,
                                                           message="Имя должно быть от 3 до 100 символов")])
    email = StringField("Email: ", validators=[DataRequired("Обязательное поле"),
                                               Email("Некорректный email")])
    psw1 = PasswordField("Пароль: ", validators=[DataRequired("Обязательное поле"),
                                                 Length(min=4, max=100,
                                                        message="Пароль должен быть от 4 до 100 символов")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired("Обязательное поле"),
                                                        EqualTo('psw1', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")


class ProfileUpdateForm(FlaskForm):
    username = StringField("Никнейм: ", validators=[Optional(),
                                                    Length(min=3, max=100,
                                                           message="Имя должно быть от 3 до 100 символов")])
    psw1 = PasswordField("Новый пароль: ", validators=[Optional(),
                                                       Length(min=4, max=100,
                                                              message="Пароль должен быть от 4 до 100 символов")])
    psw2 = PasswordField("Повтор нового пароля: ", validators=[EqualTo('psw1', message="Пароли не совпадают")])
    avatar = FileField("Обновить аватарку")
    submit = SubmitField("Внести изменения")


class AddRecipeForm(FlaskForm):
    name = StringField("Название блюда: ", validators=[DataRequired('Обязательное поле')])
    recipe = TextAreaField("Рецепт: ", validators=[Optional(),
                                                   Length(max=2000, message="Не более 2000 символов")])
    is_public = BooleanField("Сделать публичным", default=False)
    submit = SubmitField("Добавить блюдо")


class AddProductForm(FlaskForm):

    def validate(self, extra_validators=None):
        if not super(AddProductForm, self).validate():
            return False

        prots_value = self.prots.data
        fats_value = self.fats.data
        carbs_value = self.carbs.data

        total_grams = prots_value + fats_value + carbs_value

        if total_grams > 100:
            self.prots.errors.append('Сумма белков, жиров и углеводов не должна превышать 100 грамм.')
            self.fats.errors.append('Сумма белков, жиров и углеводов не должна превышать 100 грамм.')
            self.carbs.errors.append('Сумма белков, жиров и углеводов не должна превышать 100 грамм.')
            return False

        return True

    name = StringField("Название продукта: ", validators=[DataRequired('Обязательное поле')])
    kkal = FloatField("Калорий на 100г: ", validators=[input_required('Обязательное поле'),
                                                       is_float,
                                                       NumberRange(min=0.00, max=900.00,
                                                                   message="Введите корректное значение")])
    prots = FloatField("Белка на 100г: ", validators=[input_required('Обязательное поле'),
                                                      is_float,
                                                      NumberRange(min=0.00, max=100.00,
                                                                  message="Введите корректное значение")])
    fats = FloatField("Жиров на 100г: ", validators=[input_required('Обязательное поле'),
                                                     is_float,
                                                     NumberRange(min=0.00, max=100.00,
                                                                 message="Введите корректное значение")])
    carbs = FloatField("Углеводов на 100г: ", validators=[input_required('Обязательное поле'),
                                                          is_float,
                                                          NumberRange(min=0.00, max=100.00,
                                                                      message="Введите корректное значение")])
    weight = FloatField("Масса продукта в блюде в граммах: ", validators=[input_required('Обязательное поле'),
                                                                          is_float,
                                                                          NumberRange(min=0.00, max=10000.00,
                                                                                      message="Введите корректное значение (не более 10 кг)")])
    submit = SubmitField("Добавить продукт")


class RecipeUpdateForm(FlaskForm):
    name = StringField("Изменить название блюда: ", validators=[Optional()])
    recipe = TextAreaField("Изменить рецепт: ", validators=[Optional(),
                                                            Length(max=2000, message="Не более 2000 символов")])
    final_weight = FloatField("Вес готового блюда: ", validators=[Optional(),
                                                                  NumberRange(max=99999,
                                                                              message="Слишком большое число (не более 10 кг)")])
    is_public = BooleanField("Сделать/оставить публичным", default=False)
    submit = SubmitField("Обновить данные")


class CommentForm(FlaskForm):
    comment = TextAreaField("", validators=[Optional(),
                                            Length(max=1000, message="Не более 1000 символов")])
    submit = SubmitField("Оставить комментарий")
