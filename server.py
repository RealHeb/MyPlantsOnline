import flask_login
from flask import render_template, Flask, redirect, request
from flask_login import login_user, LoginManager, current_user
from data.users import User
from data.Plants import Plants
from forms.registerthing import RegisterForm
from forms.newplantthing import PlantForm
from forms.loginthing import LoginForm
from werkzeug.utils import secure_filename
from data import db_session
from flask_restful import abort
import sys
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
counter = 0


@app.route('/Главная.html')
@app.route('/')
def main_page():
    return render_template('Главная.html')


@app.route('/Регистрация.html', methods=['GET', 'POST'])
def register_page():
    if not current_user.is_authenticated:
        form = RegisterForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                password = request.form.get('password')
                password2 = request.form.get('password_again')
                email = request.form.get('email')
                login = request.form.get('name')
                if register_user_in_db(password, password2, email, login):
                    return redirect('Профиль.html')
        return render_template('Регистрация.html', form=form)
    else:
        return profile()


@app.route('/Авторизация.html', methods=['GET', 'POST'])
def auth_page():
    if not current_user.is_authenticated:
        form = LoginForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                password = request.form.get('password')
                login = request.form.get('username')
                if login_user_in_db(login, password):
                    return redirect('Профиль.html')
        return render_template('Авторизация.html', form=form)
    else:
        return profile()


@app.route('/Новый-цветок.html', methods=['GET', 'POST'])
def new_plant_page():
    form = PlantForm()
    if request.method == 'POST':
        name = form.name.data
        desc = form.description.data
        image = form.image_file.data
        filename = secure_filename(image.filename)
        file_path = os.path.dirname(sys.argv[0])
        image.save(file_path + '/static/images/' + filename)
        week = []
        if form.monday.data:
            week.append('понедельник')
        if form.tuesday.data:
            week.append('вторник')
        if form.wednesday.data:
            week.append('среду')
        if form.thursday.data:
            week.append('четверг')
        if form.friday.data:
            week.append('пятницу')
        if form.saturday.data:
            week.append('субботу')
        if form.sunday.data:
            week.append('воскресенье')
        if any(week):
            schedule = 'Поливать в ' + ', '.join(week) + '.'
        else:
            schedule = 'Не поливать.'
        add_plant_to_user(current_user.email, name, filename, desc, schedule)
        return main_page()
    return render_template('Новый-цветок.html', form=form)


@app.route('/Профиль.html', methods=['GET', 'POST'])
def profile():
    try:
        useful = current_user.plants
    except AttributeError:
        useful = []
    return render_template('Профиль.html', plants=useful)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def register_user_in_db(password, password2, email1, login):
    db_sess = db_session.create_session()
    email_used = False
    user1 = User()
    user1.name = login
    user1.set_password(password)
    user1.email = email1
    if password == password2 and email1.find('@') != -1:
        for _ in db_sess.query(User).filter(User.email == email1):
            email_used = True
        if not email_used:
            db_sess.add(user1)
            db_sess.commit()
            login_user(user1, remember=True)
            db_sess.close()
            return True
        else:
            abort(418, message=f"{email1} email already in use.")
    db_sess.close()
    return False


def login_user_in_db(email, password):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.email == email):
        if user.check_password(password):
            login_user(user, remember=True)
            return True
    db_sess.close()
    return False


def add_plant_to_user(email, plant_name, image, plant_description, plant_schedule='Не поливать'):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.email == email):
        plant = Plants(name=plant_name, description=plant_description, user1=user, schedule=plant_schedule, image=image)
        db_sess.add(plant)
        db_sess.commit()
        db_sess.close()
        return


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return main_page()


if __name__ == '__main__':
    db_session.global_init("db/WebPlant.db")
    app.run('127.0.0.1', port=8080)
