from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    make_response,
    request,
    flash,
)
from app.forms.login import LoginForm
from app.routes.auth import User
from flask_login import (
    login_required,
    login_user,
    LoginManager,
    current_user,
    logout_user,
)
import requests, json


main = Blueprint("main", __name__, url_prefix="/")


@main.route("/index")
@login_required
def index():
    is_active = True
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    response = requests.get(
        current_app.config["API_URL"] + "/linacs",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        params={"is_active": is_active, "skip": skip, "limit": limit},
    )
    linacs = json.loads(response.text)
    return render_template(
        "index.html", linacs=linacs, current_user=current_user, skip=skip, limit=limit
    )


@main.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        data = {"username": username, "password": password}
        response = requests.post(
            current_app.config["API_URL"] + "/auth/login",
            headers={"content-type": "application/json"},
            json=data,
        )
        if response.status_code == 200:
            user_data = json.loads(response.text)
            print(user_data)
            user = User(
                user_data["user"]["uid"],
                user_data["user"]["username"],
                user_data["user"]["role"],
            )
            login_user(user)
            req = make_response(redirect(url_for("main.index")))
            req.set_cookie("access_token", user_data["access_token"], httponly=True)
            return req
        else:
            flash("Usuario o contraseña incorrectos", "danger")
            return redirect(url_for("main.login"))
    return render_template("login.html", formulario=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("main.login"))
