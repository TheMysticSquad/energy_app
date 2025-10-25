from database_manager import DatabaseManager
import random
import string

class NSCDatabase(DatabaseManager):
    """Handles all NSC-specific database operations."""

    def insert_nsc_application(self, name, phone, address, category, circle, division, subdivision, section, document_path):
        """Insert new service connection request and return reference number."""
        try:
            ref_number = f"NSC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
            query = """
                INSERT INTO nsc_applications 
                (reference_number, name, phone, address, category, circle, division, subdivision, section, document_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
            """
            self._run_query(query, (
                ref_number, name, phone, address, category, circle, division, subdivision, section, document_path
            ))
            return ref_number
        except Exception as e:
            print(f"NSC Insert Error: {e}")
            return None

    def get_location_hierarchy(self):
        """Fetch Circle → Division → Subdivision → Section mapping."""
        query = """
            SELECT c.CircleName, d.DivisionName, s.SubdivisionName, sec.SectionName
            FROM Circles c
            INNER JOIN Divisions d ON c.CircleID = d.CircleID
            INNER JOIN Subdivisions s ON d.DivisionID = s.DivisionID
            INNER JOIN Sections sec ON s.SubdivisionID = sec.SubdivisionID
        """
        return self._run_query(query, fetch=True)

    # -------------------------------------------------------------------
    # 👇 New Methods for Inspection → AMISP → Profile Creation Workflow
    # -------------------------------------------------------------------

    def get_user_applications(self):
        """Fetch all NSC applications for the logged-in user (mock for now)."""
        query = "SELECT reference_number, name, category, status FROM nsc_applications ORDER BY created_at DESC"
        return self._run_query(query, fetch=True)

    def get_pending_verifications(self):
        """Return all applications pending site inspection verification."""
        query = """
            SELECT reference_number, name, phone, address, category, circle, division, subdivision, section, status
            FROM nsc_applications
            WHERE status = 'Pending'
        """
        return self._run_query(query, fetch=True)

    def get_application_by_ref(self, ref_number):
        """Fetch detailed info for a specific application."""
        query = "SELECT * FROM nsc_applications WHERE reference_number = %s"
        rows = self._run_query(query, (ref_number,), fetch=True)
        return rows[0] if rows else None

    def update_inspection(self, ref_number, load, category):
        """Update site inspection result (load & category)."""
        query = """
            UPDATE nsc_applications
            SET verified_load = %s, verified_category = %s, status = 'Verified'
            WHERE reference_number = %s
        """
        self._run_query(query, (load, category, ref_number))

    def update_amisp_response(self, ref_number, meter_number, account_number):
        """Update AMISP response (meter installed, account generated)."""
        query = """
            UPDATE nsc_applications
            SET meter_number = %s, account_number = %s, status = 'Connection Released'
            WHERE reference_number = %s
        """
        self._run_query(query, (meter_number, account_number, ref_number))
