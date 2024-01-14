from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('board', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/<string:id>')
def board(id):
    return render_template('board.html')
