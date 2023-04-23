from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class PlantForm(FlaskForm):
    name = StringField('Имя цветка', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    image_file = FileField('Картинка')
    monday = BooleanField('Понедельник')
    tuesday = BooleanField('Вторник')
    wednesday = BooleanField('Среда')
    thursday = BooleanField('Четверг')
    friday = BooleanField('Пятница')
    saturday = BooleanField('Суббота')
    sunday = BooleanField('Воскресенье')
    submit = SubmitField('Сохранить')
