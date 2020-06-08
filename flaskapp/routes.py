from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, bcrypt, db,socketio
from flask_socketio import send, emit, join_room, leave_room
from flaskapp.scripts.getpics import getPics

from flaskapp.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_required, login_user
from flaskapp.models import User

from OpenSSL import SSL
import secrets
import requests
import enchant

dictionary = enchant.Dict("en_US")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/random", methods=["GET", "POST"])
def random():
    randomword = requests.get("https://random-word-api.herokuapp.com/word?number=1").text[2:-2]
    images = getPics(randomword)

    return render_template("random.html", images=images)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account Created', "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful, Please check email and password", "danger")
    return render_template("login.html", form=form)

@app.route("/newgame")
@login_required
def newgame():
    url = secrets.token_urlsafe(8)
    return render_template("newgame.html", url=url)


@app.route("/game/<string:game_id>", methods=["GET", "POST"])
@login_required
def game(game_id):
    return render_template("game.html")

roomsAndPlayers = {}

@socketio.on("change")
def change(msg):
    room = roomsAndPlayers[msg["url"]]
    if len(room) == 2:
        roomsAndPlayers[msg["url"]].append(room[0])
    elif len(room) == 3:
        lastindex = roomsAndPlayers[msg["url"]][0:2].index(roomsAndPlayers[msg["url"]][-1])
        newindex = (lastindex - 1) * -1
        roomsAndPlayers[msg["url"]][2] = roomsAndPlayers[msg["url"]][newindex]
        emit("updated", {"current": roomsAndPlayers[msg["url"]][newindex]}, room=msg["url"])

@socketio.on("joingame")
def handle_join(msg):
    room = roomsAndPlayers.get(msg["url"])
    if room == None or room == []:
        roomsAndPlayers[msg["url"]] = [current_user.username]

    elif current_user.username in room:
        print("you are in this room")

    elif len(room) >= 2:
        print("full")
    
    elif len(room) == 1:
        roomsAndPlayers[msg["url"]].append(current_user.username)
        
    username = current_user.username
    join_room(msg["url"])
    emit("players", {"players": room[0:2]}, room=msg["url"])


@socketio.on("leavegame")
def handle_leaving(msg):
    room = roomsAndPlayers[msg["url"]]
    room.pop(room.index(current_user.username))
    if len(room) == 0:

        del roomsAndPlayers[msg["url"]]

    username = current_user.username
    leave_room(msg["url"])
    send(username + " left", room=msg["url"])
    emit("players", {"players": room}, room=msg["url"])

@socketio.on("search")
def handle_search(msg):
    search = msg["search"]
    if dictionary.check(search):
        images = getPics(search)
        emit("images", {"images": images}, room = msg["url"])
    else:
        emit("undefined", {"word": "'"+search + "' could not be found in the dictionary, try something else"}, room = msg["url"])

@socketio.on("correct")
def handle_correct(msg):
    emit("nicejob", {"info": msg["user"] + " guessed it !"}, room=msg["url"])


@socketio.on("wrong")
def handle_correct(msg):
    emit("badjob", {"info": msg["user"] + " could not guess it!"}, room=msg["url"])