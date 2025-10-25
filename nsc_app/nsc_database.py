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
            print(f" NSC Insert Error: {e}")
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
