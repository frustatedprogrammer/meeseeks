import logging
from flask import Flask
from cassandra.cqlengine import connection
from cassandra.auth import PlainTextAuthProvider
from website.models import User
from cassandra.cqlengine.management import sync_table
from flask_login import LoginManager
from website.helper.creds_helper import creds_provider,keyspace_provider
from website.helper.logging_helper import log_folder


def create_app():

    '''
    fetch the connection details of the cassandra database
    :return:
    '''
    secure_connect_bundle, client_id, client_secret = creds_provider()
    keyspace = keyspace_provider()

    connection.setup(None, keyspace, cloud={'secure_connect_bundle': secure_connect_bundle}, auth_provider= PlainTextAuthProvider(client_id, client_secret))

    '''
    create table for models in keyspace.
    add if new models are added.
    '''
    sync_table(User)

    log_folder()
    logging.basicConfig(filename=f'./log/{keyspace}.log', level=logging.INFO)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DUMMY PARAMETER'

    app.logger.info('started')

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    '''
    login manager : maintains the user status
    eg: if the user logs out, the user shouldn't be able to access the homepage.
    '''

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.objects(id=id).first()

    return app