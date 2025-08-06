from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="KPI Test API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# Read DB config from environment
mysql_url = os.getenv("MYSQL_URL")
parsed = urlparse(mysql_url)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 3306
db = parsed.path.lstrip('/')

# Function to connect to DB
def get_connection():
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )

# ===================== LOGIN API (UNCHANGED) =====================
@app.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT l.employee_id, e.name, e.role
            FROM login l
            JOIN employees e ON l.employee_id = e.employee_id
            WHERE l.email = %s 
              AND l.password_hash = SHA2(%s, 256)
        """, (email, password))
        
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        return {
            "employee_id": user_data["employee_id"],
            "name": user_data["name"],
            "role": user_data["role"],
            "message": "Login successful"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== Common Allowed Models =====================
ALLOWED_MODELS = [
    "service_connections",
    "metering",
    "billing",
    "collection",
    "disconnection_recovery",
    "theft_management"  
]

# ===================== KPI API (Dynamic) =====================
@app.get("/test/kpi")
def get_kpi(
    model: str = Query(..., description=f"Model name: {', '.join(ALLOWED_MODELS)}"),
    section_id: int = Query(..., description="Section ID"),
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)")
):
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Allowed models: {', '.join(ALLOWED_MODELS)}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = f"""
            SELECT *
            FROM `{model}`
            WHERE section_id = %s AND `year` = %s AND `month` = %s
        """
        cur.execute(query, (section_id, year, month))
        data = cur.fetchone()

        cur.close()
        conn.close()

        if not data:
            raise HTTPException(status_code=404, detail=f"No KPI data found in {model} for given parameters.")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching KPI data: {str(e)}")


# ===================== FILTERS API (NO TRAILING SLASH) =====================
@app.get("/filters")
def get_filters(employee_id: int = Query(..., description="Employee ID")):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM employees WHERE employee_id=%s""", (employee_id,))
        emp = cur.fetchone()

        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found.")

        result = {}

        if emp['role'] == 'circle':
            cur.execute("SELECT * FROM Circles WHERE CircleID=%s", (emp['circle_id'],))
            result['circle'] = cur.fetchone()

            cur.execute("SELECT * FROM Divisions WHERE CircleID=%s", (emp['circle_id'],))
            result['divisions'] = cur.fetchall()

            cur.execute("""
                SELECT s.*
                FROM Subdivisions s
                JOIN Divisions d ON s.DivisionID = d.DivisionID
                WHERE d.CircleID=%s
            """, (emp['circle_id'],))
            result['sub_divisions'] = cur.fetchall()

            cur.execute("""
                SELECT s.*
                FROM Sections s
                JOIN Divisions d ON s.DivisionID = d.DivisionID
                WHERE d.CircleID=%s
            """, (emp['circle_id'],))
            result['sections'] = cur.fetchall()

        elif emp['role'] == 'division':
            cur.execute("SELECT * FROM Circles WHERE CircleID=%s", (emp['circle_id'],))
            result['circle'] = cur.fetchone()

            cur.execute("SELECT * FROM Divisions WHERE DivisionID=%s", (emp['division_id'],))
            result['division'] = cur.fetchone()

            cur.execute("SELECT * FROM Subdivisions WHERE DivisionID=%s", (emp['division_id'],))
            result['sub_divisions'] = cur.fetchall()

            cur.execute("SELECT * FROM Sections WHERE DivisionID=%s", (emp['division_id'],))
            result['sections'] = cur.fetchall()

        elif emp['role'] == 'sub_division':
            cur.execute("SELECT * FROM Circles WHERE CircleID=%s", (emp['circle_id'],))
            result['circle'] = cur.fetchone()

            cur.execute("SELECT * FROM Divisions WHERE DivisionID=%s", (emp['division_id'],))
            result['division'] = cur.fetchone()

            cur.execute("SELECT * FROM Subdivisions WHERE SubdivisionID=%s", (emp['sub_division_id'],))
            result['sub_division'] = cur.fetchone()

            cur.execute("SELECT * FROM Sections WHERE SubdivisionID=%s", (emp['sub_division_id'],))
            result['sections'] = cur.fetchall()

        elif emp['role'] == 'section':
            cur.execute("SELECT * FROM Circles WHERE CircleID=%s", (emp['circle_id'],))
            result['circle'] = cur.fetchone()

            cur.execute("SELECT * FROM Divisions WHERE DivisionID=%s", (emp['division_id'],))
            result['division'] = cur.fetchone()

            cur.execute("SELECT * FROM Subdivisions WHERE SubdivisionID=%s", (emp['sub_division_id'],))
            result['sub_division'] = cur.fetchone()

            cur.execute("SELECT * FROM Sections WHERE SectionID=%s", (emp['section_id'],))
            result['section'] = cur.fetchone()

        else:
            raise HTTPException(status_code=400, detail="Invalid role.")

        cur.close()
        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Generic Trend API (NO TRAILING SLASH) =====================
@app.get("/trend")
def get_trend(
    model: str = Query(..., description="The name of the table"),
    section_id: int = Query(..., description="Section ID"),
    year: int = Query(..., description="Year")
):
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model specified. Allowed models: {', '.join(ALLOWED_MODELS)}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        query = f"""
            SELECT *
            FROM `{model}`
            WHERE section_id = %s AND `year` = %s
            ORDER BY `year` ASC, `month` ASC;
        """
        
        cur.execute(query, (section_id, year))
        data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for model '{model}' with the given parameters.")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data: {str(e)}")
