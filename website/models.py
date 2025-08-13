from . import db
from flask_login import UserMixin
from datetime import datetime


user_post_table = db.Table(
    "user_post_table",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    #email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    #phone = db.Column(db.String(14))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    liked_posts = db.relationship("Post", secondary=user_post_table, back_populates="users_liked")


class PrivateChat(db.Model):
    __tablename__ = "private_chat"
    id = db.Column(db.Integer, primary_key=True)
    owner1_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner2_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    own1_last_read = db.Column(db.DateTime(timezone=True))
    own2_last_read = db.Column(db.DateTime(timezone=True))


class PrivateMsg(db.Model):
    __tablename__ = "private_msg"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=datetime.now)
    text = db.Column(db.String(2000))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    private_chat_id = db.Column(db.Integer, db.ForeignKey("private_chat.id"))


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=datetime.now)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.String(2000))
    users_liked = db.relationship("User", secondary=user_post_table, back_populates="liked_posts")


"""
class ChatGroup(db.Model):
    __tablename__ = "chatgroup"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    members = db.relationship("User", secondary="user_chatgroup", back_populates="chat_groups")
    messages = db.relationship("Message")

class UserChatGroup(db.Model):
    __tablename__ = "user_chatgroup"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    chatgroup_id = db.Column(db.Integer, db.ForeignKey("chatgroup.id"), primary_key=True)

class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(2000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    chatgroup_id = db.Column(db.Integer, db.ForeignKey("chatgroup.id"))
"""