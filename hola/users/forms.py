from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from hola.models import User

class RegistrationForm(FlaskForm):
    usuario = StringField('Nombre de usuario',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    confirmar_contraseña = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('contraseña')])
    enviar = SubmitField('Registrarte')
    
    def validate_usuario(self, usuario):
        user = User.query.filter_by(usuario=usuario.data).first()
        if user:
            raise ValidationError('Este usuario ya existe. Elija otro')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya existe. Elija otro')
    
class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    recordar = BooleanField('Recordar')
    enviar = SubmitField('Iniciar sesión')
    
class UpdateAccountForm(FlaskForm):
    usuario = StringField('Nombre de usuario',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    picture = FileField('Actualizar imagen de perfil', validators=[FileAllowed(['jpg', 'png'])])
    enviar = SubmitField('Actualizar')
    
    def validate_usuario(self, usuario):
        if usuario.data != current_user.usuario:
            user = User.query.filter_by(usuario=usuario.data).first()
            if user:
                raise ValidationError('Este usuario ya existe. Elija otro')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email ya existe. Elija otro')
            
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Peticion para la recuperación de contraseña')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No hay una cuenta asociada a este email.')
        
class ResetPasswordForm(FlaskForm):
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    confirmar_contraseña = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('contraseña')])
    submit = SubmitField('Restablecer contraseña')