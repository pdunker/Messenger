from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, PrivateChat, PrivateMsg
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        user = User.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.password, password):
                #flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password.", category="error")
        else:
            flash("Username doesn't exist.", category="error")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    session["_remember"] = "clear"
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    print(" ### sign_up()")
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Enter a username")
            return render_template("sign_up.html")
        password = request.form.get("password")
        if not password:
            flash("Enter a password")
            return render_template("sign_up.html")


        user = User.query.filter_by(name=name).first()
        if user:
            flash("Username already exists", category="error")
        else:
            new_user = User(name=name,
                            password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            #flash("Account created!", category="success")

            admin = User.query.filter_by(name="Admin").first()
            private_chat = PrivateChat(owner1_id=admin.id, owner2_id=new_user.id)
            db.session.add(private_chat)
            db.session.commit()
            msg = PrivateMsg(text=f"Bem-vindo, {name}!", user_id=admin.id, private_chat_id=private_chat.id)
            db.session.add(msg)
            db.session.commit()

            return redirect(url_for("views.home"))

    return render_template("sign_up.html")
