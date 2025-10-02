from flask import Blueprint, request, jsonify
from db import get_db_connection
import psycopg2

subject_bp = Blueprint("subject", __name__)

# Add Subject
@subject_bp.route("/addsubject", methods=["POST"])
def add_subject():
    try:
        data = request.get_json()
        subject_name = data.get("subjectname")
        subject_info = data.get("subjectinfo")

        # Validate inputs
        if not subject_name or not subject_info:
            return jsonify({"error": "Both subjectname and subjectinfo are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Call stored procedure
        cur.execute("CALL sp_setsubjects(%s, %s);", (subject_name, subject_info))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Subject added successfully"}), 201

    except psycopg2.Error as e:
        # Handles PostgreSQL related errors
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        # Handles any other error
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500
