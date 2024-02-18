from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from forum.auth import login_required, validate_board
from forum.db import get_db
from forum.board import board_dict

bp = Blueprint('post', __name__)

@bp.route('/<string:board_id>/create', methods=('GET', 'POST'))
@login_required
def create(board_id):
    validate_board(board_id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, board_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], board_id)
            )
            db.commit()
            return redirect(url_for('board.board', board_id=board_id))
        
    return render_template('post/create.html', board_id=board_id)


@bp.route('/<string:board_id>/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(board_id, id):
    validate_board(board_id)
    post = get_post(id)

    if post['author_id'] != g.user['id']:
        abort(403)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('board.board', board_id=board_id))
    
    return render_template('post/update.html', post=post, board_id=board_id)


@bp.route('/<string:board_id>/<int:id>/delete', methods=('POST',))
@login_required
def delete(board_id, id):
    validate_board(board_id)
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('board.board', board_id=board_id))


@bp.route('/<string:board_id>/<int:id>', methods=('GET','POST'))
def view(board_id, id):
    validate_board(board_id)
    post = get_post(id)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Comment cannot be empty.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (author_id, post_id, body)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], id, body)
            )
            db.commit()

            return redirect(url_for('post.view', id=id, board_id=board_id))

    comments = get_comments(id)
    board_name = board_dict[board_id]

    return render_template('post/view.html', post=post, comments=comments, board_id=board_id, board_name=board_name)



def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post ID {id} does not exist.")

    #if check_author and post['author_id'] != g.user['id']:
    #    abort(403)
    
    return post


def get_comments(id):
    comments = get_db().execute(
        'SELECT c.id, c.author_id, c.created, c.body, u.username'
        ' FROM comment c'
        ' JOIN post p ON c.post_id = p.id'
        ' JOIN user u ON c.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchall()

    return comments
