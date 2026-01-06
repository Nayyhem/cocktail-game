from flask import Blueprint, render_template
from utils import get_current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)
