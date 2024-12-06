from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    request,
    flash,
)
from flask_login import login_required, current_user
import requests
import json

from app.forms.user import UserForm

users = Blueprint("users", __name__)


@users.route("/users", methods=["GET"])
@login_required
def dashboard():
    filter = request.args.get("filter")
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    response = requests.get(
        current_app.config["API_URL"] + "/users",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        params={"is_active": filter, "skip": skip, "limit": limit},
    )
    users = json.loads(response.text)
    return render_template(
        "admin_users.html",
        users=users,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@users.route("/users:<uuid:user_uid>", methods=["GET"])
@login_required
def get_user(user_uid):
    response = requests.get(
        current_app.config["API_URL"] + f"/users/{user_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    user = json.loads(response.text)
    return render_template(
        "get_user.html",
        user=user,
        current_user=current_user,
    )


@users.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        role = form.role.data
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "role": role,
            "is_active": True,
        }
        response = requests.post(
            current_app.config["API_URL"] + "/auth/create",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
            json=data,
        )
        if response.status_code == 201:
            flash("Usuario creado con éxito", "success")
        else:
            flash("Fallo al crear el usuario!", "danger")
        return redirect(url_for("users.dashboard"))
    return render_template("create_user.html", form=form)


@users.route("/user/update/<uuid:user_uid>", methods=["GET", "POST"])
@login_required
def update_user(user_uid):
    form = UserForm()
    if request.method == "POST":
        user_update_data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "username": request.form["username"],
            "role": request.form["role"],
            "is_active": request.form.get("is_active") == "on",
        }
        response = requests.patch(
            current_app.config["API_URL"] + f"/users/update/{user_uid}",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
            json=user_update_data,
        )
        if response.status_code == 200:
            flash("user actualizado con éxito!", "success")
        else:
            flash("Fallo al actualizar el usuario!", "danger")
        return redirect(url_for("users.dashboard"))

    response = requests.get(
        current_app.config["API_URL"] + f"/users/{user_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    user = json.loads(response.text)
    if response.status_code == 404:
        flash("Usuario no encontrado!", "danger")
        return redirect(url_for("users.dashboard"))

    form.first_name.data = user["first_name"]
    form.last_name.data = user["last_name"]
    form.username.data = user["username"]
    form.role.data = user["role"]
    form.is_active.data = user["is_active"]

    return render_template("update_user.html", form=form, user=user)


@users.route("/users/delete/<user_uid>")
@login_required
def delete_user(user_uid):
    response = requests.delete(
        current_app.config["API_URL"] + f"/users/delete/{user_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 404:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("users.dashboard"))
    flash("Usuario eliminado.", "success")
    return redirect(url_for("users.dashboard"))


@users.route("/users/activate/<uuid:user_uid>")
@login_required
def activate_user(user_uid):
    data = {"is_active": True}
    response = requests.patch(
        current_app.config["API_URL"] + f"/users/update/{user_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        json=data,
    )
    if response.status_code == 200:
        flash("Estado del usuario actualizado.", "success")
        return redirect(url_for("users.dashboard"))
    else:
        flash("Fallo al actualizar el estado del usuario.", "danger")
    return redirect(url_for("users.dashboard"))


@users.route("/users/deactivate/<uuid:user_uid>")
@login_required
def deactivate_user(user_uid):
    data = {"is_active": False}
    response = requests.patch(
        current_app.config["API_URL"] + f"/users/update/{user_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        json=data,
    )
    if response.status_code == 200:
        flash("Estado del usuario actualizado.", "success")
    else:
        flash("Fallo al actualizar el estado del usuario.", "danger")
    return redirect(url_for("users.dashboard"))
