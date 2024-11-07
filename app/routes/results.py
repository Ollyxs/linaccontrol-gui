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

results = Blueprint("results", __name__)


@results.route("/results", methods=["GET"])
@login_required
def view_results():
    response = requests.get(
        current_app.config["API_URL"] + "/results",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 200:
        results_data = json.loads(response.text)

        # Obtener nombres del acelerador y de las personas
        for result in results_data:
            # Obtener el nombre del acelerador
            linac_response = requests.get(
                current_app.config["API_URL"] + f"/linacs/{result['linac_uid']}",
                headers={
                    "content-type": "application/json",
                    "authorization": "Bearer " + request.cookies["access_token"],
                },
            )
            if linac_response.status_code == 200:
                linac_data = json.loads(linac_response.text)
                result["linac_name"] = linac_data["name"]
            else:
                result["linac_name"] = "Desconocido"

            # Obtener el nombre de la persona que realizó el test
            realized_by_response = requests.get(
                current_app.config["API_URL"] + f"/users/{result['realized_by']}",
                headers={
                    "content-type": "application/json",
                    "authorization": "Bearer " + request.cookies["access_token"],
                },
            )
            if realized_by_response.status_code == 200:
                realized_by_data = json.loads(realized_by_response.text)
                result["realized_by_name"] = realized_by_data["username"]
            else:
                result["realized_by_name"] = "Desconocido"

            # Obtener el nombre de la persona que revisó el test (si existe)
            if result["reviewed_by"]:
                reviewed_by_response = requests.get(
                    current_app.config["API_URL"] + f"/users/{result['reviewed_by']}",
                    headers={
                        "content-type": "application/json",
                        "authorization": "Bearer " + request.cookies["access_token"],
                    },
                )
                if reviewed_by_response.status_code == 200:
                    reviewed_by_data = json.loads(reviewed_by_response.text)
                    result["reviewed_by_name"] = reviewed_by_data["username"]
                else:
                    result["reviewed_by_name"] = "Desconocido"
            else:
                result["reviewed_by_name"] = None

        return render_template("view_results.html", results=results_data)
    else:
        flash("Error al cargar los resultados.", "danger")
        return redirect(url_for("main.index"))


@results.route("/results/<result_uid>", methods=["GET"])
@login_required
def view_result_details(result_uid):
    response = requests.get(
        current_app.config["API_URL"] + f"/results/{result_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 200:
        result_data = json.loads(response.text)
        print("#########\nresult_data: ", result_data, "\n#########")

        # Obtener el nombre del acelerador
        linac_response = requests.get(
            current_app.config["API_URL"] + f"/linacs/{result_data['linac_uid']}",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
        )
        if linac_response.status_code == 200:
            linac_data = json.loads(linac_response.text)
            print("#########\nlinac_data: ", linac_data, "\n#########")
            result_data["linac_name"] = linac_data["name"]
        else:
            flash("Error al cargar el nombre del acelerador.", "danger")
            return redirect(url_for("results.view_results"))

        # Obtener los nombres de las pruebas
        for test_result in result_data["tests"]:
            test_response = requests.get(
                current_app.config["API_URL"] + f"/tests/{test_result['test_uid']}",
                headers={
                    "content-type": "application/json",
                    "authorization": "Bearer " + request.cookies["access_token"],
                },
            )
            if test_response.status_code == 200:
                test_data = json.loads(test_response.text)
                print("#########\ntest_data: ", test_data, "\n#########")
                test_result["test_name"] = test_data["test_name"]
            else:
                flash("Error al cargar el nombre de la prueba.", "danger")
                return redirect(url_for("results.view_results"))

        # Obtener el nombre de la persona que realizó el test
        realized_by_response = requests.get(
            current_app.config["API_URL"] + f"/users/{result_data['realized_by']}",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer " + request.cookies["access_token"],
            },
        )
        if realized_by_response.status_code == 200:
            realized_by_data = json.loads(realized_by_response.text)
            result_data["realized_by_name"] = realized_by_data["username"]
        else:
            flash(
                "Error al cargar el nombre de la persona que realizó el test.", "danger"
            )
            return redirect(url_for("results.view_results"))

        # Obtener el nombre de la persona que revisó el test (si existe)
        if result_data["reviewed_by"]:
            reviewed_by_response = requests.get(
                current_app.config["API_URL"] + f"/users/{result_data['reviewed_by']}",
                headers={
                    "content-type": "application/json",
                    "authorization": "Bearer " + request.cookies["access_token"],
                },
            )
            if reviewed_by_response.status_code == 200:
                reviewed_by_data = json.loads(reviewed_by_response.text)
                result_data["reviewed_by_name"] = reviewed_by_data["username"]
            else:
                flash(
                    "Error al cargar el nombre de la persona que revisó el test.",
                    "danger",
                )
                return redirect(url_for("results.view_results"))
        else:
            result_data["reviewed_by_name"] = None

        return render_template("view_result_details.html", result=result_data)
    else:
        flash("Error al cargar los resultados.", "danger")
        return redirect(url_for("results.view_results"))


@results.route("/results/<result_uid>/review", methods=["POST"])
@login_required
def review_result(result_uid):
    if current_user.role not in ["admin", "fisico"]:
        flash("No tiene permisos para revisar este resultado.", "danger")
        return redirect(url_for("results.view_result_details", result_uid=result_uid))

    response = requests.patch(
        current_app.config["API_URL"] + f"/results/review/{result_uid}",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + request.cookies["access_token"],
        },
    )
    if response.status_code == 200:
        flash("Resultado revisado correctamente.", "success")
    else:
        flash("Error al revisar el resultado.", "danger")
    return redirect(url_for("results.view_result_details", result_uid=result_uid))
