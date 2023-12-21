import os

DB_HOST = os.environ.get('DB_HOST', "localhost")
DB_PORT = os.environ.get('DB_PORT', 3306)
DB_NAME = os.environ.get('MYSQL_DATABASE', "DustyDollar")
DB_USER = os.environ.get('MYSQL_USER', 'sherrif')
DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'maverick')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', "super-secret-key")
