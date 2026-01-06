from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from models import db, User
from utils import get_current_user, login_required

bp = Blueprint('auth', __name__)
ph = PasswordHasher()

REGISTER_TEMPLATE = 'register.html'

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        # Validations
        if not username or not email or not password:
            flash('Remplissez tous les champs.', 'danger')
            return render_template(REGISTER_TEMPLATE, form=request.form)
        if password != password2:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template(REGISTER_TEMPLATE, form=request.form)
        if User.query.filter_by(username=username).first():
            flash('Nom d\'utilisateur déjà pris.', 'danger')
            return render_template(REGISTER_TEMPLATE, form=request.form)
        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé.', 'danger')
            return render_template(REGISTER_TEMPLATE, form=request.form)

        # Hashage du mot de passe
        try:
            pw_hash = ph.hash(password)
        except (ValueError, TypeError) as _e:
            flash('Erreur lors du hashage du mot de passe.', 'danger')
            return render_template(REGISTER_TEMPLATE, form=request.form)

        user = User(username=username, email=email, password_hash=pw_hash, wins=0)
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès. Connectez-vous.', 'success')
        return redirect(url_for('auth.login'))

    return render_template(REGISTER_TEMPLATE, form={})

LOGIN_TEMPLATE = 'login.html'

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('Remplissez tous les champs.', 'danger')
            return render_template(LOGIN_TEMPLATE, form=request.form)

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user:
            flash('Utilisateur introuvable.', 'danger')
            return render_template(LOGIN_TEMPLATE, form=request.form)

        try:
            if not ph.verify(user.password_hash, password):
                flash('Mot de passe incorrect.', 'danger')
                return render_template(LOGIN_TEMPLATE, form=request.form)
        except argon2_exceptions.VerifyMismatchError:
            # le hash ne correspond pas
            flash('Mot de passe incorrect.', 'danger')
            return render_template(LOGIN_TEMPLATE, form=request.form)

        # Connexion réussie
        session.clear()
        session['user_id'] = user.id
        flash('Connecté avec succès.', 'success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('auth.dashboard'))

    return render_template(LOGIN_TEMPLATE, form={})


@bp.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    if not user:
        abort(404)
    return render_template('dashboard.html', user=user)
