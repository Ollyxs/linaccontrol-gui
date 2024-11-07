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

from app.forms.linac import LinacForm

admin = Blueprint("users", __name__)


@admin.route("/users", methods=["GET"])
@login_required
def dashboard():
    # filter = request.args.get("filter")
    # skip = request.args.get("skip", 0, type=int)
    # limit = request.args.get("limit", 10, type=int)

    response = requests.get(
        current_app.config["API_URL"] + "/users",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        # params={"is_active": filter, "skip": skip, "limit": limit},
    )
    linacs = json.loads(response.text)
    return render_template(
        "admin.html",
        linacs=linacs,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@admin.route("/admin/linac_uid:<linac_uid>", methods=["GET"])
@login_required
def get_linac(linac_uid):
    response = requests.get(
        current_app.config["API_URL"] + f"/linacs/{linac_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    linac = json.loads(response.text)
    return render_template(
        "get_linac.html",
        linac=linac,
        current_user=current_user,
    )


@admin.route("/admin/create", methods=["GET", "POST"])
@login_required
def create_linac():
    form = LinacForm()
    if form.validate_on_submit():
        name = form.name.data
        data = {"name": name, "is_active": True}
        response = requests.post(
            current_app.config["API_URL"] + "/linacs/create",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
            json=data,
        )
        if response.status_code == 201:
            flash("Acelerador creado con éxito", "success")
        else:
            flash("Fallo al crear el acelerador!", "danger")
        return redirect(url_for("admin.dashboard"))
    return render_template("create_linac.html", form=form)


@admin.route("/admin/update/<uuid:linac_uid>", methods=["GET", "POST"])
@login_required
def update_linac(linac_uid):
    if request.method == "POST":
        linac_update_data = {
            "name": request.form["name"],
            "is_active": request.form.get("is_active") == "on",
        }
        response = requests.patch(
            current_app.config["API_URL"] + f"/linacs/update/{linac_uid}",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
            json=linac_update_data,
        )
        if response.status_code == 200:
            flash("Linac updated successfully!", "success")
        else:
            flash("Failed to update linac!", "danger")
        return redirect(url_for("admin.dashboard"))

    response = requests.get(
        current_app.config["API_URL"] + f"/linacs/{linac_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    linac = json.loads(response.text)
    if response.status_code == 404:
        flash("Linac not found!", "danger")
        return redirect(url_for("admin.dashboard"))
    return render_template("update_linac.html", linac=linac)


@admin.route("/admin/delete/<linac_uid>")
@login_required
def delete_linac(linac_uid):
    response = requests.delete(
        current_app.config["API_URL"] + f"/linacs/delete/{linac_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 404:
        flash("Acelerador no encontrado", "danger")
        return redirect(url_for("admin.dashboard"))
    flash("Acelerador eliminado.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/activate_linac/<linac_uid>")
@login_required
def activate_linac(linac_uid):
    data = {"is_active": True}
    response = requests.patch(
        current_app.config["API_URL"] + f"/linacs/update/{linac_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        json=data,
    )
    if response.status_code == 200:
        flash("Estado del acelerador actualizado.", "success")
        return redirect(url_for("admin.dashboard"))
    else:
        flash("Fallo al actualizar el estado del acelerador.", "danger")
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/deactivate_linac/<linac_uid>")
@login_required
def deactivate_linac(linac_uid):
    data = {"is_active": False}
    response = requests.patch(
        current_app.config["API_URL"] + f"/linacs/update/{linac_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
        json=data,
    )
    if response.status_code == 200:
        flash("Linac status updated successfully!", "success")
    else:
        flash("Failed to update linac status!", "danger")
    return redirect(url_for("admin.dashboard"))
