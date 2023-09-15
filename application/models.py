from .database import db
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    no_of_followers = db.Column(db.Integer)
    no_of_posts = db.Column(db.Integer)
    profile_photo = db.Column(db.String)
    
class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String)
    caption_description = db.Column(db.String)
    image_url = db.Column(db.String)
    timestamp = db.Column(DateTime(timezone = True), default = func.now(),onupdate = func.now())
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String)

class UserRelation(db.Model):
    __tablename__ = 'user_relation'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    follower_id = db.Column(db.Integer)
    following_id = db.Column(db.Integer)
    follower_username = db.Column(db.String)
    following_username = db.Column(db.String)