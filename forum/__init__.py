import os

from flask import Flask

from . import db, auth, board, post


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(board.bp)
    app.register_blueprint(post.bp)
    app.add_url_rule('/', endpoint='index')
    
    
    return app
