from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-b4-deploy?"
socketio = SocketIO(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.sql"
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from flaskapp import routes

if __name__=="__main__":
    app.run()