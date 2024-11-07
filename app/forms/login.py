from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, validators

msg = "Campo Obligatorio"


class LoginForm(FlaskForm):
    username = StringField(
        "Usuario",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                max=12, message="El usuario debe tener como máximo 12 caracteres"
            ),
        ],
    )
    password = PasswordField(
        "Contraseña",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                min=8, message="La contraseña debe tener al menos 6 caracteres"
            ),
        ],
    )
    submit = SubmitField("Ingresar")
