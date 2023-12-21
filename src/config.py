from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from src.env_variables import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, JWT_SECRET_KEY
from src.services.db_service import SQLAlchemyDBService

db_url = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

db_interface = SQLAlchemyDBService(db_url=db_url)