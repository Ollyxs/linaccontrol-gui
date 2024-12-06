from datetime import datetime
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

# from flask_cors import CORS
import requests, json


test = Blueprint("test", __name__)
# CORS(test)


@test.route("/test/<linac_uid>/<frequency>", methods=["GET"])
@login_required
def test_suite(linac_uid, frequency):
    date_str = request.args.get("date")
    if not date_str:
        date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))

    response = requests.get(
        current_app.config["API_URL"]
        + "/test_suites/"
        + str(linac_uid)
        + "/"
        + str(frequency)
        + "?date="
        + date_str,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    test_suite_test = json.loads(response.text)
    if response.status_code == 200:
        return render_template(
            "test.html",
            current_date=datetime.strptime(date_str, "%Y-%m-%d"),
            linac=test_suite_test["linac"],
            test_suite=test_suite_test["test_suite"],
            test_suite_tests=test_suite_test["test_suite_tests"],
            frequency=test_suite_test["frequency"],
            result_uid=test_suite_test.get("result_uid"),
            result=test_suite_test.get("result"),
        )
    elif response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "Missing results for dates" in error_detail:
            missing_dates = (
                error_detail.split(": ")[1].strip("[]").replace("'", "").split(", ")
            )
            flash(
                f"Faltan resultados para las fechas: {', '.join(missing_dates)}.",
                "danger",
            )
            flash(
                f"Se muestra el formulario para la fecha {missing_dates[0]}. Debe completar este formulario antes de agregar un test para la fecha actual.",
                "info",
            )
            return redirect(
                url_for(
                    "test.test_suite",
                    linac_uid=linac_uid,
                    frequency=frequency,
                    date=missing_dates[0],
                )
            )
        elif "Results already exist for this date" in error_detail:
            flash("Los resultados ya existen para esta fecha.", "danger")
            return redirect(url_for("main.index"))
    else:
        flash("Error al cargar el test o el test no existe.", "danger")
    return redirect(url_for("main.index"))


@test.route("/test/submit", methods=["POST"])
@login_required
def test_suite_submit():
    print("request.form: ", request.form)
    linac_uid = request.form["linac_uid"]
    test_suite_uid = request.form["test_suite_uid"]
    result = request.form["observations"]
    frequency_uid = request.form["frequency_uid"]
    created_at = request.form.get("created_at", datetime.now().strftime("%Y-%m-%d"))
    test_results_data = [
        {"test_uid": key.split("[")[1].split("]")[0], "result": request.form[key]}
        for key in request.form.keys()
        if key.startswith("test_results_data")
    ]

    formatted_data = {
        "result_data": {
            "linac_uid": linac_uid,
            "test_suite_uid": test_suite_uid,
            "result": result,
            "frequency_uid": frequency_uid,
            "created_at": created_at,
        },
        "test_results_data": test_results_data,
    }

    response = requests.post(
        current_app.config["API_URL"] + "/results",
        json=formatted_data,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 201:
        flash("Resultados enviados correctamente", "success")
        return redirect(url_for("main.index"))
    elif response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "Missing results for dates" in error_detail:
            missing_dates = (
                error_detail.split(": ")[1].strip("[]").replace("'", "").split(", ")
            )
            flash(
                f"Faltan resultados para las fechas: {', '.join(missing_dates)}.\nSe muestra el formulario para la fecha {missing_dates[0]}",
                "danger",
            )
            return redirect(
                url_for(
                    "test.test_suite",
                    linac_uid=linac_uid,
                    frequency=frequency,
                    date=missing_dates[0],
                )
            )
        elif "Results already exist for this date" in error_detail:
            flash("Los resultados ya existen para esta fecha.", "danger")
            return redirect(url_for("main.index"))
    else:
        flash("Error al enviar los resultados", "danger")
        return redirect(url_for("main.index"))


@test.route("/test/update", methods=["POST"])
@login_required
def test_suite_update():
    result_uid = request.form["result_uid"]
    linac_uid = request.form["linac_uid"]
    test_suite_uid = request.form["test_suite_uid"]
    result = request.form["observations"]
    frequency_uid = request.form["frequency_uid"]
    updated_at = request.form.get("created_at", datetime.now().strftime("%Y-%m-%d"))
    test_results_data = [
        {"test_uid": key.split("[")[1].split("]")[0], "result": request.form[key]}
        for key in request.form.keys()
        if key.startswith("test_results_data")
    ]

    formatted_data = {
        "result_update_data": {
            "linac_uid": linac_uid,
            "test_suite_uid": test_suite_uid,
            "result": result,
            "frequency_uid": frequency_uid,
            "updated_at": updated_at,
            "reviewed_by": current_user.uid,
        },
        "test_results_data": test_results_data,
    }

    response = requests.patch(
        current_app.config["API_URL"] + "/results/" + str(result_uid),
        json=formatted_data,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 200:
        flash("Resultados actualizados correctamente", "success")
        return redirect(url_for("main.index"))
    else:
        flash("Error al actualizar los resultados", "danger")
    return redirect(url_for("main.index"))
