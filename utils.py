from flask import session, flash, redirect, url_for, render_template, request
from functools import wraps
from models import User, db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)

def page_not_found(_e):
    return render_template('404.html'), 404

def internal_error(_e):
    return render_template('500.html'), 500

def add_win():
    """Incrémente le nombre de victoires de l'utilisateur connecté."""
    user = get_current_user()
    if user:
        user.wins += 1
        db.session.commit()