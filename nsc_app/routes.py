# nsc_app/routes.py
from flask import render_template, request, jsonify, Blueprint
import os
from .nsc_database import NSCDatabase

nsc_blueprint = Blueprint("nsc", __name__)
db = NSCDatabase()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Landing page for NSC
@nsc_blueprint.route('/apply-new-connection', methods=['GET'])
def apply_form():
    return render_template('dashboard/nsc/apply-new-connection.html')

