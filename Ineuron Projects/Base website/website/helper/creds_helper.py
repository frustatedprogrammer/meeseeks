import yaml
import yamlordereddictloader

'''
returns the cassandara connection details.
'''


def read_yaml():
    config_path = './config/config.yaml'
    app_config = yaml.load(open(config_path), Loader=yamlordereddictloader.Loader)
    return app_config


def creds_provider():
    app_config = read_yaml()
    secure_connect_bundle = app_config['website']['secure_bundle']
    client_id = app_config['website']['token']['client_id']
    client_secret = app_config['website']['token']['client_secret']
    return secure_connect_bundle, client_id, client_secret


def keyspace_provider():
    app_config = read_yaml()
    return app_config['website']['keyspace']
