from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, validators

msg = "Campo Obligatorio"


class LinacForm(FlaskForm):
    name = StringField(
        "Nombre",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                max=50, message="El nombre debe tener como máximo 50 caracteres"
            ),
        ],
    )
    submit = SubmitField("Crear")
