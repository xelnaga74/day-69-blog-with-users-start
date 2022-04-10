from flask import Flask, render_template, redirect, url_for, flash, request, abort, Response
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
from database import *
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.app_context().push()
# db.create_all()
# create_record(first_user)
# create_record(first_post)


login_manager = LoginManager()
login_manager.init_app(app)


def get_gravatar_url(email: str) -> str:
    email_to_hash = email.strip().lower()
    hash_ = hashlib.md5(email_to_hash.encode()).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{hash_}"
    print(gravatar_url)
    return gravatar_url


app.jinja_env.globals.update(get_gravatar_url=get_gravatar_url)


# Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def user_logged_in():
    return dict(logged_in=current_user.is_authenticated)


@app.context_processor
def is_admin():
    if not current_user.is_anonymous and current_user.id == 1:
        return dict(is_admin=True)
    else:
        return dict(is_admin=False)


def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if not current_user.is_anonymous and current_user.id == 1:
            print("is admin")
            return function(*args, **kwargs)
        else:
            print("not admin")
            abort(403)
    return wrapper_function


# Routes
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if read_user(request.form["email"]):
            flash("That email already exists. Please log in.")
            return redirect(url_for("login"))
        else:
            hash_ = generate_password_hash(password=request.form["password"], method="pbkdf2:sha256", salt_length=8)
            new_user = User(name=request.form["name"],
                            email=request.form["email"],
                            password=hash_)
            create_record(new_user)
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = read_user(email)
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Wrong password. Please Try again.")
        else:
            flash("That email does not exist. Please Try again.")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if request.method == "POST":
        if not current_user.is_anonymous and current_user.is_authenticated:
            text = request.form["text"]
            if text:
                new_comment = Comment(
                    text=text,
                    author=current_user,
                    post=read_post(post_id)
                )
                create_record(new_comment)
                return redirect(url_for("show_post", post_id=post_id))
            else:
                pass
        else:
            flash("Please log in.")
    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post")
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post_to_edit/<int:post_id>")
@admin_only
def edit_post(post_id):
    post_to_edit = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        img_url=post_to_edit.img_url,
        author=post_to_edit.author,
        body=post_to_edit.body
    )
    if edit_form.validate_on_submit():
        post_to_edit.title = edit_form.title.data
        post_to_edit.subtitle = edit_form.subtitle.data
        post_to_edit.img_url = edit_form.img_url.data
        # post_to_edit.author = edit_form.author.data
        post_to_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_to_edit.id))

    return render_template("make-post_to_edit.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    p1 = read_user("xelnaga74@gmail.com")
    c1 = read_post(1)
    print(p1.posts)
    for post in p1.posts:
        print(post.title)
    print(c1.author)
    print(c1.author.name)

    app.run(host='0.0.0.0', port=5000)
