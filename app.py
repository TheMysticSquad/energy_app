# /workspaces/energy_app/app.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os


from utility_api_server import router as api_router 


# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 


# -----------------------------
# FastAPI App Initialization
# -----------------------------
app = FastAPI(title="Utility CIS Backend", version="1.0")

# 1. SERVE STATIC FILES (CSS, JS)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 2. INCLUDE API ROUTES (All your API endpoints are now under /api/v1/)
app.include_router(api_router, prefix="/api/v1")


# -----------------------------
# 3. FRONTEND ROUTE (Serves index.html from templates)
# -----------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Serves the main HTML file."""
    try:
        with open(os.path.join(BASE_DIR, "templates", "login.html"), "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: Frontend login.html not found!</h1>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard():
    """Serves the dashboard.html after successful (simulated) login."""
    try:
        with open(os.path.join(BASE_DIR, "templates", "dashboard.html"), "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: Dashboard file not found!</h1>", status_code=500)
        
# 🎯 CATCH-ALL ROUTE FOR MODULE PAGES (Kept from previous steps to handle module links)
@app.get("/{module_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_module_page(module_path: str):
    """
    Serves a placeholder page for any path not explicitly defined 
    (e.g., /service/new, /billing/run)
    """
    if module_path.startswith("static/"):
        # Allow static files to be handled by app.mount
        return 
        
    page_title = module_path.replace("/", " > ").title()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CIS - {page_title}</title>
        <style>body{{font-family: sans-serif; padding: 30px;}} h1{{color: #007bff;}} .back{{margin-top: 20px; display: block;}}</style>
    </head>
    <body>
        <h1>{page_title} Module</h1>
        <p>This is the landing page for the **{page_title}** process.</p>
        <p>Example Next Step: Create a new file like <code>templates/{module_path}.html</code>.</p>
        <a href="/dashboard" class="back">← Back to Dashboard</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# -----------------------------
# 4. Run Server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)