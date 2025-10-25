from flask import Blueprint, request, jsonify
import os
from .nsc_database import NSCDatabase

api_blueprint = Blueprint("nsc_api", __name__)
db = NSCDatabase()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fetch Circle → Division → Subdivision → Section
@api_blueprint.route('/locations', methods=['GET'])
def get_locations():
    try:
        rows = db.get_location_hierarchy()
        hierarchy = {}
        for circle, division, subdivision, section in rows:
            hierarchy.setdefault(circle, {}).setdefault(division, {}).setdefault(subdivision, []).append(section)
        return jsonify(hierarchy)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Submit NSC application
@api_blueprint.route('/submit-nsc', methods=['POST'])
def submit_nsc():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        category = request.form.get('category')
        circle = request.form.get('circle')
        division = request.form.get('division')
        subdivision = request.form.get('subdivision')
        section = request.form.get('section')

        file = request.files.get('document')
        file_path = None
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

        ref_number = db.insert_nsc_application(
            name, phone, address, category, circle, division, subdivision, section, file_path
        )

        if ref_number:
            return jsonify({"success": True, "reference_number": ref_number})
        return jsonify({"success": False, "message": "Error while saving application"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
