# /workspaces/energy_app/app.py
from flask import Flask, render_template, send_from_directory
import os

# Import your NSC blueprint
from nsc_app.routes import nsc_blueprint
from nsc_app.api import api_blueprint           # JSON APIs


# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# Flask App Initialization
# -----------------------------
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))

# Register your NSC Blueprint
# All NSC URLs will be under /service/nsc/
app.register_blueprint(nsc_blueprint, url_prefix="/service/nsc")
app.register_blueprint(api_blueprint, url_prefix="/api/nsc")  # NOT /nsc/api

# -----------------------------
# 1. Serve Static Files (CSS, JS)
# -----------------------------
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

# -----------------------------
# 2. Root and Dashboard Pages
# -----------------------------
@app.route('/')
def serve_frontend():
    """Serves login page."""
    try:
        return render_template('login.html')
    except Exception:
        return "<h1>Error: login.html not found!</h1>", 500


@app.route('/dashboard')
def serve_dashboard():
    """Serves dashboard page."""
    try:
        return render_template('dashboard.html')
    except Exception:
        return "<h1>Error: dashboard.html not found!</h1>", 500

# -----------------------------
# 3. Catch-all Fallback Route
# -----------------------------
@app.route('/<path:module_path>')
def serve_module_page(module_path):
    """
    Serves a placeholder for undefined module routes.
    """
    # Avoid catching static or NSC routes
    if module_path.startswith(("static/", "service/nsc/")):
        return "", 404

    page_title = module_path.replace("/", " > ").title()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CIS - {page_title}</title>
        <style>body{{font-family:sans-serif;padding:30px;}}
        h1{{color:#007bff;}}.back{{margin-top:20px;display:block;}}</style>
    </head>
    <body>
        <h1>{page_title} Module</h1>
        <p>This is the landing page for the <b>{page_title}</b> process.</p>
        <p>Example Next Step: Create a new file like 
        <code>templates/{module_path}.html</code>.</p>
        <a href="/dashboard" class="back">← Back to Dashboard</a>
    </body>
    </html>
    """
    return html_content




# -----------------------------
# 4. Run the Flask App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
