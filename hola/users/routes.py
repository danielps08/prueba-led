from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from hola import db, bcrypt
from hola.models import User, Post
from hola.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from hola.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.contraseña.data).decode('utf-8')
        user = User(usuario=form.usuario.data, email=form.email.data, contraseña=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Tu cuenta ha sido creada', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.contraseña, form.contraseña.data):
            login_user(user, remember=form.recordar.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Email o contraseña incorrecta', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/cuenta', methods=['GET', 'POST'])
@login_required
def cuenta():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.usuario = form.usuario.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Su cuenta ha sido actualizada', 'success')
        return redirect(url_for('users.cuenta'))
    elif request.method == 'GET':
        form.usuario.data = current_user.usuario
        form.email.data = current_user.email
    image_file = url_for('static', filename='imagenes/' + current_user.image_file)
    return render_template('cuenta.html', title='Cuenta', image_file=image_file, form=form)

@users.route('/user/<string:usuario>')
def user_posts(usuario):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(usuario=usuario).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Se envio un email para restablecer su contraseña', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('El token es inválido o ha expirado', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.contraseña.data).decode('utf-8')
        user.contraseña = hashed_password
        db.session.commit()
        flash('Su contraseña ha sido actualizada', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)