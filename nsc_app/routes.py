# nsc_app/routes.py
from flask import render_template, request, jsonify, Blueprint
import os
from .nsc_database import NSCDatabase

nsc_blueprint = Blueprint("nsc", __name__)
db = NSCDatabase()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# NSC Application Form
@nsc_blueprint.route('/apply-new-connection', methods=['GET'])
def apply_form():
    return render_template('nsc/apply-new-connection.html')

# View Status Page
@nsc_blueprint.route('/view-status', methods=['GET'])
def view_status():
    return render_template('nsc/view-status.html')

# Verification Listing
@nsc_blueprint.route('/verify', methods=['GET'])
def verify_list():
    return render_template('nsc/verify-applications.html')

# Application Detail for Verification
@nsc_blueprint.route('/verify/<ref_no>', methods=['GET'])
def verify_details(ref_no):
    return render_template('nsc/application-details.html', ref_no=ref_no)
# Dashboard for NSC Module
@nsc_blueprint.route('/dashboard', methods=['GET'])
def nsc_dashboard():
    return render_template('nsc/nsc_dashboard.html')
    