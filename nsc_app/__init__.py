from flask import Flask
from .routes import nsc_blueprint

# Make sure template_folder points to the absolute location
import os
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

flask_app = Flask(__name__, template_folder=template_dir)
flask_app.config['SECRET_KEY'] = 'your-secret-key'

flask_app.register_blueprint(nsc_blueprint, url_prefix="/nsc")
