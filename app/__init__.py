from flask import Flask
from app.routes import bp as routes_bp
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(routes_bp)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes