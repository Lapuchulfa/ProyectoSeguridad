import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import db, Usuario

auth = Blueprint('auth', __name__)

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home_dashboard'))
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        if not correo or not password:
            flash('Por favor completa todos los campos.', 'warning')
            return render_template('auth/login.html')
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect(url_for('dashboard.home_dashboard'))
        flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home_dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        if not nombre or not correo or not password:
            flash('Por favor completa todos los campos.', 'warning')
            return render_template('auth/register.html')
        if not EMAIL_RE.match(correo):
            flash('Formato de correo electrónico inválido.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('auth/register.html')
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.', 'danger')
            return render_template('auth/register.html')
        nuevo = Usuario(
            nombre=nombre,
            correo=correo,
            password=generate_password_hash(password)
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Cuenta creada exitosamente. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            nombre = request.form.get('nombre', '').strip()
            correo = request.form.get('correo', '').strip()
            if not nombre or not correo:
                flash('Nombre y correo son obligatorios.', 'warning')
                return render_template('auth/perfil.html')
            if not EMAIL_RE.match(correo):
                flash('Formato de correo electrónico inválido.', 'danger')
                return render_template('auth/perfil.html')
            existing = Usuario.query.filter_by(correo=correo).first()
            if existing and existing.id != current_user.id:
                flash('Ese correo ya está registrado por otro usuario.', 'danger')
                return render_template('auth/perfil.html')
            current_user.nombre = nombre
            current_user.correo = correo
            db.session.commit()
            flash('Perfil actualizado exitosamente.', 'success')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')
            if not check_password_hash(current_user.password, current_pw):
                flash('La contraseña actual es incorrecta.', 'danger')
                return render_template('auth/perfil.html')
            if len(new_pw) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
                return render_template('auth/perfil.html')
            if new_pw != confirm_pw:
                flash('Las contraseñas no coinciden.', 'warning')
                return render_template('auth/perfil.html')
            current_user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash('Contraseña cambiada exitosamente.', 'success')

        return redirect(url_for('auth.perfil'))
    return render_template('auth/perfil.html')
