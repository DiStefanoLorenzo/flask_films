#auth.py
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask import current_app   # definisce il contesto del modulo
from flask_login import login_user, login_required, logout_user, current_user  # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
import uuid

from models.conn import db
from models.model import *
import asyncio

from data.scraper import get_films

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login():
    # shows the login form page
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # manages the login form post request
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    stmt = db.select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalar_one_or_none()
    # user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    current_app.logger.info(f'user {user}')
    if not user or not user.check_password(password):
        current_app.logger.error(f' user {email} not logged with password {password}')
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('auth.base'))

@auth.route('/home/')
@login_required
def base():
    #lista = get_films()
    #film = invia_richiesta_post(10)
    #f1 = Film(film)
    return render_template('home2.html')#,films=lista)

@auth.route('/get_films/')
@login_required
def get_films_route():
    films = get_films()
    films_json = []
    for film in films:
        films_json.append(film.to_dict())

    return films_json  # Serializziamo gli oggetti in JSON

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/login.html')

@login_required
def generate_api_key():
    api_key = str(uuid.uuid4())
    current_user.set_api_key(api_key) # Imposta la nuova API Key
    return redirect(url_for('auth.profile'))

@auth.route('/profile')
@login_required
def profile():
    api_keys = (User.query.filter_by(email=current_user.email).first()).get_api_keys()
    return render_template('auth/profile.html', api_keys=api_keys)

@auth.route('/signup', methods=["GET"])
def signup():
    return render_template('auth/signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # signup input validation and logic
    #TODO verify password strenght
    username = request.form["username"] #as an alternative use request.form.get("username")
    email = request.form["email"]    
    password = request.form["password"]
    current_app.logger.debug(f'Password: "{password}"')

    if not username:
        flash('Invalid username')
        return redirect(url_for('auth.signup'))
    if not email:
        flash('Invalid email')
        return redirect(url_for('auth.signup'))
    if not password:
        flash('Invalid password')
        return redirect(url_for('auth.signup'))                
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user: 
        flash('User with this email address already exists')
        return redirect(url_for('auth.signup'))
    
    api_key = str(uuid.uuid4())

    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    user.set_api_key(api_key) # Imposta la nuova API Key
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()

    return redirect(url_for('auth.login'))
