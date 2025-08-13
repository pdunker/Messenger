from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from .models import User, PrivateChat, PrivateMsg, Post
from . import db
import json
from datetime import datetime
from markupsafe import escape
#from twilio.rest import Client


views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
@views.route("/home", methods=["GET", "POST"])
def home():
    print(" ### home() request.method:", request.method, "at:", datetime.now())

    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        post_txt = request.form.get("post")
        if post_txt != "":
            new_post = Post(owner_id=current_user.id, text=post_txt)
            db.session.add(new_post)
            db.session.commit()
        else:
            flash("Post can't be blank!")

    posts = db.session.query(Post).all()
    posts.reverse()
    for post in posts:
        user = User.query.filter_by(id=post.owner_id).first()
        post.user_name = user.name
        print(f"post: {post.id}, text: {post.text}, users_liked: {post.users_liked}")

    return render_template("home.html", posts=posts)


@views.route("/inbox", methods=["GET", "POST"])
@login_required
def inbox():
    print(" ### inbox() request.method:", request.method, "at:", datetime.now())

    # sending a message and creating a private_chat if necessary:
    if request.method == "POST":
        msg = request.form.get("message")

        if len(msg) < 1:
            flash("No message was written.", category="error")
        else:
            chat_user_id = session["chat_user_id"]
            private_chat = (PrivateChat.query.filter_by(owner1_id=current_user.id, owner2_id=chat_user_id).first() or
                            PrivateChat.query.filter_by(owner1_id=chat_user_id, owner2_id=current_user.id).first())
            if not private_chat:
                private_chat = PrivateChat(owner1_id=current_user.id, owner2_id=chat_user_id)
                db.session.add(private_chat)
                db.session.commit()

            msg = PrivateMsg(text=msg, user_id=current_user.id, private_chat_id=private_chat.id)
            db.session.add(msg)
            db.session.commit()

            to_user = User.query.filter_by(id=chat_user_id).first()
#           send_whatsapp_msg(current_user, to_user)

    # getting all users to display the list, excluding current user:
    users = db.session.query(User).all()
    for user in users:
        if user.name == current_user.name:
            users.remove(user)

    # creating a dict with all chats last message:
    pvt_chats_last_msgs = {}
    pvt_chats_unread = {}
    for user in users:
        pvt_chat = get_private_chat(current_user.id, user.id)
        if pvt_chat:
            messages = PrivateMsg.query.filter_by(private_chat_id=pvt_chat.id).all()
            last_pvt_msg = messages[len(messages) - 1]
            pvt_chats_last_msgs[user.name] = last_pvt_msg.text
            if last_pvt_msg.user_id == user.id:
                if pvt_chat.owner1_id == current_user.id:
                    my_chat_last_read = pvt_chat.own1_last_read
                else:
                    my_chat_last_read = pvt_chat.own2_last_read
                if my_chat_last_read is None or my_chat_last_read < last_pvt_msg.date:
                    pvt_chats_unread[user.name] = True

    # getting all the messages between the current user and a user he has chosen:
    messages = None
    chat_user_id = session.get("chat_user_id")
    if chat_user_id:
        pvt_chat = get_private_chat(current_user.id, chat_user_id)
        if pvt_chat:
            messages = PrivateMsg.query.filter_by(private_chat_id=pvt_chat.id).all()

    return render_template("inbox.html",
                           user=current_user,
                           users=users,
                           messages=messages,
                           pvt_chats_last_msgs=pvt_chats_last_msgs,
                           pvt_chats_unread=pvt_chats_unread)

@views.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    user = User.query.filter_by(name=username).first()

    if not user:
        return "User '%s'" % escape(username) + " doesn't exist."

    user.posts = Post.query.filter_by(owner_id=user.id).all()
    return render_template("user.html",
                           user=user)


@views.route("/chat", methods=["POST"])
@login_required
def chat():
    print(" ### chat() method:", request.method, "at:", datetime.now())

    if request.method == "POST":
        form = json.loads(request.data)
        user_id = form["user_id"]
        if session.get("chat_user_id") == user_id:
            session.pop("chat_user_name")
            session.pop("chat_user_id")
        else:
            user = User.query.filter_by(id=user_id).first()
            session["chat_user_name"] = user.name
            session["chat_user_id"] = user_id
            pvt_chat = get_private_chat(current_user.id, user_id)
            if pvt_chat:
                if pvt_chat.owner1_id == current_user.id:
                    pvt_chat.own1_last_read = datetime.now()
                else:
                    pvt_chat.own2_last_read = datetime.now()
                db.session.commit()

    return redirect(url_for("views.inbox"))


@views.route("/like", methods=["POST"])
@login_required
def like():
    print(" ### like() method:", request.method, "at:", datetime.now())
    form = json.loads(request.data)
    post_id = form["post_id"]
    post = Post.query.filter_by(id=post_id).first()
    if post in current_user.liked_posts:
        current_user.liked_posts.remove(post)
    else:
        current_user.liked_posts.append(post)
    db.session.commit()
    return redirect(url_for("views.home"))


def get_private_chat(user_id_1, user_id_2):
    return (PrivateChat.query.filter_by(owner1_id=user_id_1, owner2_id=user_id_2).first() or
            PrivateChat.query.filter_by(owner1_id=user_id_2, owner2_id=user_id_1).first())


"""
def send_whatsapp_msg(from_user, to_user):
    account_sid = ""
    auth_token = ""
    client = Client(account_sid, auth_token)

    client.messages.create(
        from_="",
        body="Hello {to_username}, ".format(to_username=to_user.name) +
             "you have received a message "
             "from {from_username} at Messenger!\n".format(from_username=from_user.name) +
             "Go check it out at pdunker.pythonanywhere.com!",
        to="whatsapp:"+to_user.phone,
    )
"""
