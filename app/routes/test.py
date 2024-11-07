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
    response = requests.get(
        current_app.config["API_URL"]
        + "/test_suites/"
        + str(linac_uid)
        + "/"
        + str(frequency),
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    test_suite_test = json.loads(response.text)
    print("test_suite_test: ", test_suite_test)
    if response.status_code == 200:
        return render_template(
            "test.html",
            current_date=datetime.now(),
            linac=test_suite_test["linac"],
            test_suite=test_suite_test["test_suite"],
            test_suite_tests=test_suite_test["test_suite_tests"],
        )
    else:
        flash("Error al cargar el test o el test no existe.", "danger")
    return redirect(url_for("main.index"))


@test.route("/test/submit", methods=["POST"])
@login_required
def test_suite_submit():
    data = request.get_json()
    print("Data: ", data)
    if not data:
        print("No data")
    linac_uid = data["result_data"]["linac_uid"]
    test_suite_uid = data["result_data"]["test_suite_uid"]
    result = data["result_data"]["result"]
    test_results_data = data["test_results_data"]

    response = requests.post(
        current_app.config["API_URL"] + "/results",
        json={
            "result_data": {
                "linac_uid": linac_uid,
                "test_suite_uid": test_suite_uid,
                "result": result,
            },
            "test_results_data": test_results_data,
        },
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    print("response status_code: ", response.status_code)
    print("response: ", response.text)
    if response.status_code == 201:
        print("Test creado correctamente")
        flash("Test creado correctamente", "success")
        return redirect(url_for("main.index"))
    else:
        flash("Error al crear el test", "danger")
        return redirect(url_for("main.index"))
