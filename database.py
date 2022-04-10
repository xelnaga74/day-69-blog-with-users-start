from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from typing import Union
import os
from dotenv import load_dotenv

load_dotenv(".env")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

db = SQLAlchemy()


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "blog_users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    posts = db.relationship("BlogPost", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("blog_users.id"), nullable=False)
    comments = db.relationship("Comment", backref="post", lazy=True)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("blog_users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"), nullable=False)


# db management
def create_record(data: Union[User, BlogPost, Comment]):
    db.session.add(data)
    db.session.commit()


def read_user(email: str) -> User:
    return User.query.filter_by(email=email).first()


def read_post(post_id: int) -> BlogPost:
    return BlogPost.query.filter_by(id=post_id).first()


# initial data
first_user = User(
    name="xelnaga74",
    email="xelnaga74@gmail.com",
    password=generate_password_hash(password=ADMIN_PASSWORD, method="pbkdf2:sha256", salt_length=8)
)
first_post = BlogPost(
    title="The Life of Cactus",
    subtitle="Who knew that cacti lived such interesting lives.",
    date="October 20, 2020",
    body="""<p>Nori grape silver beet broccoli kombu beet greens fava bean potato quandong celery.</p>

<p>Bunya nuts black-eyed pea prairie turnip leek lentil turnip greens parsnip.</p>

<p>Sea lettuce lettuce water chestnut eggplant winter purslane fennel azuki bean earthnut pea sierra leone bologi leek soko chicory celtuce parsley j&iacute;cama salsify.</p>
""",
    img_url="https://images.unsplash.com/photo-1530482054429-cc491f61333b?ixlib=rb-1.2.1&ixid"
            "=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1651&q=80",
    author=first_user
)