from flask import Flask
from flask_cors import CORS
from config import Config
from .routes import api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    return app

__all__ = ['create_app']