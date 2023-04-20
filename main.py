from flask import render_template, Flask, redirect, request
from flask_login import login_user, LoginManager, current_user
from data.users import User
from data.Plants import Plants
from forms.registerthing import RegisterForm
from forms.newplantthing import PlantForm
from forms.loginthing import LoginForm
from data import db_session
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/Главная.html')
@app.route('/')
@app.route('/logout')
def main_page():
    return render_template('Главная.html')


@app.route('/base.html')
def test_page():
    return render_template('base.html')


@app.route('/Регистрация.html', methods=['GET', 'POST'])
def register_page():
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


@app.route('/Авторизация.html', methods=['GET', 'POST'])
def auth_page():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            password = request.form.get('password')
            login = request.form.get('username')
            if login_user_in_db(login, password):
                return redirect('Профиль.html')
    return render_template('Авторизация.html', form=form)


@app.route('/Новый-цветок.html', methods=['GET', 'POST'])
def new_plant_page():
    form = PlantForm()
    if request.method == 'POST':
        name = form.name.data
        desc = form.description.data
        image = form.image_file.data
        mond = form.monday.data
        tues = form.tuesday.data
        wens = form.wednesday.data
        thus = form.thursday.data
        fri = form.friday.data
        sat = form.saturday.data
        sun = form.sunday.data
        week = [mond, tues, wens, thus, fri, sat, sun]
        for_storage = ''
        for i in week:
            if i:
                for_storage += '1'
            else:
                for_storage += '0'
        print(for_storage)
        add_plant_to_user(current_user.email, name, desc, for_storage, image)
        return profile()
    return render_template('Новый-цветок.html', form=form)


@app.route('/Профиль.html', methods=['GET', 'POST'])
def profile():
    return render_template('Профиль.html')


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
        for user in db_sess.query(User).filter(User.email == email1):
            email_used = True
        if not email_used:
            db_sess.add(user1)
            db_sess.commit()
            login_user(user1, remember=True)
            db_sess.close()
            return True
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


def add_plant_to_user(email, plant_name, plant_description, plant_schedule='0000000', image='image/default-logo.png'):
    db_sess = db_session.create_session()
    print(email)
    for user in db_sess.query(User).filter(User.email == email):
        print(user, 'aloha')
        plant = Plants(name=plant_name, description=plant_description, user1=user, schedule=plant_schedule, image=image)
        db_sess.add(plant)
        db_sess.commit()
        db_sess.close()
        return



if __name__ == '__main__':
    db_session.global_init("db/WebPlant.db")
    app.run('127.0.0.1', port=8080)
