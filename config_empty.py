class BaseConfig(object):
    DEBUG = False
    TESTING = False
    HOST = '127.0.0.1'
    PORT = 5000
    PSQL_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_data' password='********'"
    PSQL_ADMIN_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_admin' password='********'"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    API_KEY='****************************************************************'
    HOST = '127.0.0.1'
    PORT = 5000


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    API_KEY='****************************************************************'
    HOST = '127.0.0.1'
    PORT = 8080

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    API_KEY='****************************************************************'
    HOST = '0.0.0.0'
    PORT = 8001

