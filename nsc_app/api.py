# nsc_app/api.py
from flask import Blueprint, jsonify, request
from .nsc_database import NSCDatabase

api_blueprint = Blueprint("nsc_api", __name__)
db = NSCDatabase()

# ✅ Existing APIs ----------------------------------

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
            file_path = f"uploads/{file.filename}"
            file.save(file_path)

        ref_number = db.insert_nsc_application(name, phone, address, category, circle, division, subdivision, section, file_path)
        if ref_number:
            return jsonify({"success": True, "reference_number": ref_number})
        return jsonify({"success": False, "message": "Error saving application"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ✅ New APIs ---------------------------------------

# Get applications for logged-in user (mock for now)
@api_blueprint.route('/my-applications', methods=['GET'])
def my_applications():
    apps = db.get_user_applications()
    return jsonify(apps)

# Get all pending verifications
@api_blueprint.route('/pending-verifications', methods=['GET'])
def pending_verifications():
    pending = db.get_pending_verifications()
    return jsonify(pending)

# Get full details for one application
@api_blueprint.route('/application/<ref_no>', methods=['GET'])
def application_details(ref_no):
    app = db.get_application_by_ref(ref_no)
    if not app:
        return jsonify({"error": "Application not found"}), 404
    return jsonify(app)

# Submit inspection result and send to AMISP
@api_blueprint.route('/submit-inspection', methods=['POST'])
def submit_inspection():
    data = request.json
    ref_no = data.get("reference_number")
    load = data.get("verified_load")
    category = data.get("verified_category")

    db.update_inspection(ref_no, load, category)
    # simulate AMISP
    db.update_amisp_response(ref_no, meter_number=f"MTR{ref_no[-4:]}", account_number=f"AC{ref_no[-4:]}")

    return jsonify({"success": True, "message": f"Application {ref_no} sent to AMISP."})
