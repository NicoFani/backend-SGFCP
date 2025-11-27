from .db import db
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from .config import Config

# Initialize extensions
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Import models to ensure they're registered
    from . import models
    
    # Register blueprints
    from .routes import (
        driver_bp, truck_bp, trip_bp, expense_bp,
        advance_payment_bp, app_user_bp, client_bp,
        commission_percentage_bp, driver_truck_bp,
        km_rate_bp, load_owner_bp, monthly_summary_bp, auth_bp
    )
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(driver_bp)
    app.register_blueprint(truck_bp)
    app.register_blueprint(trip_bp)  
    app.register_blueprint(expense_bp)
    app.register_blueprint(advance_payment_bp)
    app.register_blueprint(app_user_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(commission_percentage_bp)
    app.register_blueprint(driver_truck_bp)
    app.register_blueprint(km_rate_bp)
    app.register_blueprint(load_owner_bp)
    app.register_blueprint(monthly_summary_bp)
    
    return app
