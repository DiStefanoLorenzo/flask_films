import requests, json, random, string, uuid
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from routes.auth import auth as bp_auth
from models.conn import db
from models.model import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))



admin = Admin(app, name='Admin dashboard', template_mode='bootstrap4')
admin.add_view(ProtectedModelView(User, db.session))
admin.add_view(ProtectedModelView(ApiKey, db.session))

app.register_blueprint(bp_auth, url_prefix='/auth')

migrate = Migrate(app, db)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Chiama init_db durante l'inizializzazione
with app.app_context():
    init_db()  # ====================== Quando si crea un nuovo DB commentare questo elemento.
    pass

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    # return User.query.get(int(user_id))   # legacy
    return user

@app.route('/')
def home():
    return redirect(url_for('auth.login')) 

@app.route('/createuser', methods=["POST"])
#def create_user(username, email, password):
def create_user():
    values = request.json
    username = values['username']
    email = values['email']
    password = values['password']
    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()
    return (f"Utente {username} creato con successo.")

def find_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user

def test_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)

    # Verifica della password
    userChecked = find_user_by_username(username)
    return user.check_password(userChecked.password)

def add_request_to_DB(request):
    request = Request(request=request)
    db.session.add(request)
    db.session.commit()
    return "Aggiunto correttamente"



@app.route('/api/data', methods=['GET'])
def get_data():
    send_key = request.headers.get('X-API-Key')
    api_key = ApiKey.query.filter_by(value=send_key).first()
    if api_key == send_key:
        login_user(api_key.user)
        return {'data': 'Success'}
    else:
        return {'error': 'Invalid API key'}, 401

if __name__ == '__main__':
    app.run(debug=True)