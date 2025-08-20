from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from .config import Config

db = SQLAlchemy()

# Factory pattern for app creation
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Import and register blueprints here
    from .routes.driver import driver_bp
    from .routes.truck import truck_bp
    from .routes.trip import trip_bp
    from .routes.expense import expense_bp
    app.register_blueprint(driver_bp)
    app.register_blueprint(truck_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(expense_bp)
    # ...otros blueprints
    return app
