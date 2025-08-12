from fastapi import FastAPI, HTTPException, Query, Body, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
import os
import pymysql
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Load env vars
load_dotenv()

app = FastAPI(title="KPI Test API")

# CORS setup (open for UAT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL config
mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise RuntimeError("MYSQL_URL not set in environment")
parsed = urlparse(mysql_url)
DB_USER = parsed.username
DB_PASSWORD = parsed.password
DB_HOST = parsed.hostname
DB_PORT = parsed.port or 3306
DB_NAME = parsed.path.lstrip('/')

# JWT config with defaults for local dev
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))

ALLOWED_MODELS = [
    "service_connections", "metering", "billing",
    "collection", "disconnection_recovery", "theft_management"
]

def get_connection():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, cursorclass=pymysql.cursors.DictCursor
    )

# JWT utils
def create_access_token(data: dict, expires_minutes: int = JWT_EXPIRE_MINUTES):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split()[1]
    return decode_access_token(token)

def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# DB helper
def row_exists(cur, table: str, id_col: str, id_val):
    cur.execute(f"SELECT 1 FROM `{table}` WHERE `{id_col}` = %s LIMIT 1", (id_val,))
    return cur.fetchone() is not None

# ---------------- LOGIN ----------------
@app.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT l.employee_id, e.name, e.role
                FROM login l
                JOIN employees e ON l.employee_id = e.employee_id
                WHERE l.email = %s AND l.password_hash = SHA2(%s, 256)
                LIMIT 1
            """, (email, password))
            user_data = cur.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({
            "employee_id": user_data["employee_id"],
            "role": user_data["role"]
        })
        return {**user_data, "access_token": token, "token_type": "bearer"}
    finally:
        conn.close()

# ---------------- ADMIN LOGIN ----------------
@app.post("/admin/login")
def admin_login(email: str = Body(...), password: str = Body(...)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT l.employee_id, e.name, e.role
                FROM login l
                JOIN employees e ON l.employee_id = e.employee_id
                WHERE l.email = %s AND l.password_hash = SHA2(%s, 256)
                LIMIT 1
            """, (email, password))
            admin_data = cur.fetchone()

        if not admin_data or admin_data["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access denied")

        token = create_access_token({
            "employee_id": admin_data["employee_id"],
            "role": "admin"
        })

        return {
            "message": "Admin login successful",
            "access_token": token,
            "token_type": "bearer",
            "employee_id": admin_data["employee_id"],
            "role": "admin"
        }

    finally:
        conn.close()

# ---------------- KPI DATA ----------------
@app.get("/test/kpi")
def get_kpi(model: str, section_id: int, year: int, month: int):
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail="Invalid model name")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT * FROM `{model}`
                WHERE section_id=%s AND year=%s AND month=%s LIMIT 1
            """, (section_id, year, month))
            data = cur.fetchone()
        if not data:
            raise HTTPException(status_code=404, detail="No KPI data found")
        return data
    finally:
        conn.close()

# ---------------- FILTERS ----------------
@app.get("/filters")
def get_filters(employee_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get employee record
            cur.execute("SELECT * FROM employees WHERE employee_id=%s", (employee_id,))
            emp = cur.fetchone()
            if not emp:
                raise HTTPException(status_code=404, detail="Employee not found")

            circle = None
            divisions = []
            sub_divisions = []
            sections = []

            # If employee has circle_id, fetch it
            if emp.get("circle_id"):
                cur.execute("SELECT CircleID, CircleName FROM circles WHERE CircleID=%s", (emp["circle_id"],))
                circle = cur.fetchone()

            # Fetch all divisions in that circle
            if emp.get("circle_id"):
                cur.execute("SELECT DivisionID, DivisionName FROM divisions WHERE CircleID=%s", (emp["circle_id"],))
                divisions = cur.fetchall()

            # Fetch subdivisions for those divisions
            if divisions:
                div_ids = [d["DivisionID"] for d in divisions]
                cur.execute(f"SELECT SubdivisionID, SubdivisionName, DivisionID FROM subdivisions WHERE DivisionID IN ({','.join(['%s']*len(div_ids))})", div_ids)
                sub_divisions = cur.fetchall()

            # Fetch sections for those subdivisions
            if sub_divisions:
                sub_ids = [sd["SubdivisionID"] for sd in sub_divisions]
                cur.execute(f"SELECT SectionID, SectionName, SubdivisionID FROM sections WHERE SubdivisionID IN ({','.join(['%s']*len(sub_ids))})", sub_ids)
                sections = cur.fetchall()

            return {
                "circle": circle,
                "divisions": divisions,
                "sub_divisions": sub_divisions,
                "sections": sections
            }

    finally:
        conn.close()

# ---------------- ADMIN USER MGMT ----------------
@app.get("/admin/users")
def list_users(_: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees")
            return {"users": cur.fetchall()}
    finally:
        conn.close()

@app.post("/admin/users")
def add_user(name: str, email: str, password: str, role: str,
             circle_id: int = None, division_id: int = None,
             sub_division_id: int = None, section_id: int = None,
             _: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            allowed_roles = {"admin", "circle", "division", "sub_division", "section"}
            if role not in allowed_roles:
                raise HTTPException(status_code=400, detail="Invalid role")
            cur.execute("SELECT 1 FROM login WHERE email=%s", (email,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already exists")
            cur.execute("""
                INSERT INTO employees (name, role, circle_id, division_id, sub_division_id, section_id)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (name, role, circle_id, division_id, sub_division_id, section_id))
            emp_id = cur.lastrowid
            cur.execute("""
                INSERT INTO login (employee_id, email, password_hash)
                VALUES (%s, %s, SHA2(%s, 256))
            """, (emp_id, email, password))
        conn.commit()
        return {"message": "User added", "employee_id": emp_id}
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

@app.put("/admin/users/{employee_id}")
def update_user(employee_id: int, name: str = None, role: str = None, password: str = None,
                _: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            updates, params = [], []
            if name:
                updates.append("name=%s"); params.append(name)
            if role:
                updates.append("role=%s"); params.append(role)
            if updates:
                cur.execute(f"UPDATE employees SET {', '.join(updates)} WHERE employee_id=%s", (*params, employee_id))
            if password:
                cur.execute("UPDATE login SET password_hash=SHA2(%s,256) WHERE employee_id=%s", (password, employee_id))
        conn.commit()
        return {"message": "User updated"}
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

@app.delete("/admin/users/{employee_id}")
def delete_user(employee_id: int, _: dict = Depends(require_admin)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM login WHERE employee_id=%s", (employee_id,))
            cur.execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
        conn.commit()
        return {"message": "User deleted"}
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
