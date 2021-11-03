import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from hola import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/imagenes', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Solicitud de restablecimiento de contraseña', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''Para restablecer su contraseña visitar el siguiente link:
{url_for('reset_token', token=token, _external=True)}

Si usted no realizo esta solicitud simplemente ignore el mensaje.
'''
    mail.send(msg)