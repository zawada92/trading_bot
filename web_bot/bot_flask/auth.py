import datetime
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.views import View
from werkzeug.security import check_password_hash, generate_password_hash

from bot_flask.dbutil import User, get_db


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not email:
            error = "Email is required."

        if error is None:
            try:
                user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    created=datetime.datetime.now(),
                )
                db.session.add(user)
                db.session.commit()
            except db.IntegrityError:
                print("tomasz tutj lapie")
                error = "User {} is already registered.".format(username)
            else:
                return redirect(url_for("index"))

        flash(error)

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@auth_bp.before_app_request
def load_logged_in_user():
    """Binds currently logged in user to global g object"""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


def login_required(view: View) -> View:
    """Decorator function to check if a user is logged in
    before loading a view.

    Params:
        view: View which needs logged in user

    Returns:
        View: Redirected view for not logged in users and
            correct content if logged in.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
