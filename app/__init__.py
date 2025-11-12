from .db import db
from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Import models to ensure they're registered
    from . import models
    
    # Register blueprints
    from .routes import driver_bp, truck_bp, trip_bp, expense_bp
    app.register_blueprint(driver_bp)
    app.register_blueprint(truck_bp)
    app.register_blueprint(trip_bp)  
    app.register_blueprint(expense_bp)
    
    return app
