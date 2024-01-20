from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from forum.auth import login_required
from forum.db import get_db

bp = Blueprint('board', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/<string:board_id>')
def board(board_id):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, u.username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.board_id = ?'
        ' ORDER BY created DESC',
        [board_id]
    ).fetchall()
    return render_template('board.html', board_id=board_id, posts=posts)
