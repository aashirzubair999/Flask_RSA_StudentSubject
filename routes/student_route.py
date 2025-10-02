from flask import Blueprint, request, jsonify
from db import get_db_connection
from rsa_utils import encrypt_name, decrypt_name
import logging

student_bp = Blueprint("student", __name__)

# Add Student
@student_bp.route("/addstudent", methods=["POST"])
def add_student():
    try:
        data = request.get_json()
        student_name = data.get("studentname")
        subject_id = data.get("subjectid")

        if not student_name or not subject_id:
            return jsonify({"error": "Missing studentname or subjectid"}), 400

        encrypted_name = encrypt_name(student_name)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CALL sp_setstudentbysubjectid(%s, %s);", (subject_id, encrypted_name))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Student added successfully"})
    except Exception as e:
        logging.error(f"Error adding student: {e}")
        return jsonify({"error": "Failed to add student"}), 500

# Get all students by subject
@student_bp.route("/all/<int:subjectid>", methods=["GET"])
def get_students(subjectid):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN")
        cur.execute("CALL sp_getstudentbysubjectid(%s, %s);", (subjectid, "refcursor1"))
        cur.execute("FETCH ALL FROM refcursor1;")
        rows = cur.fetchall()
        cur.execute("CLOSE refcursor1")
        conn.commit()
        cur.close()
        conn.close()

        students = []
        for r in rows:
            try:
                encrypted_name = r[1]  # This should be bytes
                students.append({
                    "id": r[0],
                    "name": decrypt_name(encrypted_name),
                    "subjectid": r[2]
                })
            except Exception as e:
                logging.error(f"Error decrypting student {r[0]}: {e}")
                students.append({
                    "id": r[0],
                    "name": "[Decryption Error]",
                    "subjectid": r[2]
                })

        return jsonify(students)
    except Exception as e:
        logging.error(f"Error fetching students: {e}")
        return jsonify({"error": "Failed to fetch students"}), 500

# Get single student
@student_bp.route("/<int:studentid>", methods=["GET"])
def get_student(studentid):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Use EXACTLY the same pattern as your working route
        cur.execute("BEGIN")
        cur.execute("CALL sp_getstudentbystudentid(%s, %s);", (studentid, "refcursor1"))  # Same cursor name
        cur.execute("FETCH ALL FROM refcursor1;")  # Same cursor name
        rows = cur.fetchall()  # Use fetchall() instead of fetchone()
        cur.execute("CLOSE refcursor1")  # Same cursor name
        conn.commit()
        cur.close()
        conn.close()

        # Since we're fetching by student ID, there should be 0 or 1 row
        if rows and len(rows) > 0:
            row = rows[0]  # Take the first row
            student = {
                "id": row[0], 
                "name": decrypt_name(row[1]), 
                "subjectid": row[2]
            }
            return jsonify(student)
        return jsonify({"error": "Student not found"}), 404
        
    except Exception as e:
        logging.error(f"Error fetching student {studentid}: {e}")
        return jsonify({"error": "Failed to fetch student"}), 500


# Update student 
@student_bp.route("/update/<int:studentid>", methods=["PUT"])
def update_student(studentid):
    try:
        data = request.get_json()
        student_name = data.get("studentname")
        subject_id = data.get("subjectid")

        if not student_name or not subject_id:
            return jsonify({"error": "Missing studentname or subjectid"}), 400

        encrypted_name = encrypt_name(student_name)

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("CALL sp_updatestudentbystudentid(%s, %s, %s);", 
                   (studentid, subject_id, encrypted_name))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Student updated successfully"})
        
    except Exception as e:
        logging.error(f"Error updating student {studentid}: {e}")
        return jsonify({"error": "Failed to update student", "details": str(e)}), 500