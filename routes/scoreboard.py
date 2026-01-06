from flask import Blueprint, render_template, request
from models import User
from utils import login_required

bp = Blueprint('scoreboard', __name__)


@bp.route('/scoreboard', methods=['GET'])
@login_required
def scoreboard():
    if request.method == 'GET':
        players = User.query.order_by(User.wins.desc()).limit(50).all()
        return render_template('scoreboard.html', players=players)
    return None
