import os
from flask import Flask, render_template, url_for

def create_app(test_config=None):
    from . import utils

    #create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path,'boatapp.sqlite'),
        UPLOAD_FOLDER = os.path.join(app.root_path,'static/uploads/images'),
        MOLLIE_PUBLIC_URL = 'https://4927-2a02-a45c-27c9-1-7854-4e08-136a-508.ngrok-free.app',
        MOLLIE_API_KEY = 'test_y2G7vKvQSQajNz25V2yWGu396SbjsF'
    )

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')

    from . import reservations
    app.register_blueprint(reservations.bp)

    from . import control
    app.register_blueprint(control.bp)

    return app

