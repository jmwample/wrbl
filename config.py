class BaseConfig(object):
    DEBUG = False
    TESTING = False
    HOST = '127.0.0.1'
    PORT = 5000
    PSQL_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_data' password='5A&q*#7*&'"
    PSQL_ADMIN_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_admin' password='2Q2fzHV*D@D!'"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    HOST = '127.0.0.1'
    PORT = 6000


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    HOST = '127.0.0.1'
    PORT = 8080

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    HOST = '0.0.0.0'
    PORT = 9000

