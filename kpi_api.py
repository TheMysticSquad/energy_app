from fastapi import FastAPI, HTTPException, Query
from urllib.parse import urlparse
import os
import pymysql
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="KPI Test API")

# Read from environment
mysql_url = os.getenv("MYSQL_URL")
parsed = urlparse(mysql_url)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 3306
db = parsed.path.lstrip('/')

def get_connection():
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/test/kpi/")
def get_kpis(
    section_id: int = Query(..., description="Section ID"),
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)")
):
    data = {}

    try:
        conn = get_connection()
        cur = conn.cursor()

        # service_connections
        cur.execute("""
            SELECT * FROM service_connections 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['service_connections'] = cur.fetchone()

        # metering
        cur.execute("""
            SELECT * FROM metering 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['metering'] = cur.fetchone()

        # billing
        cur.execute("""
            SELECT * FROM billing 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['billing'] = cur.fetchone()

        # collection
        cur.execute("""
            SELECT * FROM collection 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['collection'] = cur.fetchone()

        # disconnection_recovery
        cur.execute("""
            SELECT * FROM disconnection_recovery 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['disconnection_recovery'] = cur.fetchone()

        cur.close()
        conn.close()

        if not any(data.values()):
            raise HTTPException(status_code=404, detail="No KPI data found for given parameters.")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filters/")
def get_filters(employee_id: int = Query(..., description="Employee ID")):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # find employee & role
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
