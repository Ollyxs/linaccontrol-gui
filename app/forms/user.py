from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, BooleanField, validators

msg = "Campo Obligatorio"


class UserForm(FlaskForm):
    first_name = StringField(
        "Nombre",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                max=50, message="El nombre debe tener como máximo 50 caracteres"
            ),
        ],
    )
    last_name = StringField(
        "Apellido",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                max=50, message="El apellido debe tener como máximo 50 caracteres"
            ),
        ],
    )
    username = StringField(
        "Usuario",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                max=50, message="El usuario debe tener como máximo 50 caracteres"
            ),
        ],
    )
    password = StringField(
        "Contraseña",
        [
            validators.DataRequired(message=msg),
            validators.Length(
                min=6, message="La contraseña debe tener al menos 8 caracteres"
            ),
            validators.Length(
                max=50, message="La contraseña debe tener como máximo 50 caracteres"
            ),
        ],
    )
    role = SelectField(
        "Rol",
        choices=[("admin", "Admin"), ("fisico", "Fisico"), ("tecnico", "Tecnico")],
        validators=[validators.DataRequired(message=msg)],
    )
    is_active = BooleanField("Activo")
    submit = SubmitField("Crear")
