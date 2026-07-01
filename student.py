# student.py
# Student CRUD operations

from database import Database


# -------------------------------------------------
# ADD STUDENT
# -------------------------------------------------
def add_student(name, age, gender, course, email, phone, address):
    db = Database()

    try:
        if not db.connect():
            return False, "Database connection failed."

        query = """
        INSERT INTO students
        (name, age, gender, course, email, phone, address)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        db.cursor.execute(query, (
            name,
            age,
            gender,
            course,
            email,
            phone,
            address
        ))

        db.connection.commit()

        return True, "Student added successfully."

    except Exception as e:
        return False, str(e)

    finally:
        db.close_connection()


# -------------------------------------------------
# GET ALL STUDENTS
# -------------------------------------------------
def get_all_students():
    db = Database()

    try:
        if not db.connect():
            return []

        db.cursor.execute(
            "SELECT * FROM students ORDER BY student_id DESC"
        )

        return db.cursor.fetchall()

    except Exception as e:
        print(e)
        return []

    finally:
        db.close_connection()


# -------------------------------------------------
# SEARCH STUDENTS
# -------------------------------------------------
def search_students(keyword=None, department=None):

    db = Database()

    try:
        if not db.connect():
            return []

        query = "SELECT * FROM students WHERE 1=1"
        values = []

        if keyword:
            query += """
            AND (
                CAST(student_id AS CHAR) LIKE %s
                OR name LIKE %s
                OR email LIKE %s
                OR phone LIKE %s
            )
            """

            like = f"%{keyword}%"

            values.extend([
                like,
                like,
                like,
                like
            ])

        if department:
            query += " AND course=%s"
            values.append(department)

        query += " ORDER BY student_id DESC"

        db.cursor.execute(query, tuple(values))

        return db.cursor.fetchall()

    except Exception as e:
        print(e)
        return []

    finally:
        db.close_connection()


# -------------------------------------------------
# UPDATE STUDENT
# -------------------------------------------------
def update_student(student_id,
                   name,
                   age,
                   gender,
                   course,
                   email,
                   phone,
                   address):

    db = Database()

    try:
        if not db.connect():
            return False, "Database connection failed."

        query = """
        UPDATE students
        SET
            name=%s,
            age=%s,
            gender=%s,
            course=%s,
            email=%s,
            phone=%s,
            address=%s
        WHERE student_id=%s
        """

        db.cursor.execute(query, (
            name,
            age,
            gender,
            course,
            email,
            phone,
            address,
            student_id
        ))

        db.connection.commit()

        return True, "Student updated successfully."

    except Exception as e:
        return False, str(e)

    finally:
        db.close_connection()


# -------------------------------------------------
# DELETE STUDENT
# -------------------------------------------------
def delete_student(student_id):

    db = Database()

    try:
        if not db.connect():
            return False, "Database connection failed."

        db.cursor.execute(
            "DELETE FROM students WHERE student_id=%s",
            (student_id,)
        )

        db.connection.commit()

        return True, "Student deleted successfully."

    except Exception as e:
        return False, str(e)

    finally:
        db.close_connection()


# -------------------------------------------------
# TOTAL STUDENT COUNT
# -------------------------------------------------
def get_total_student_count():

    db = Database()

    try:
        if not db.connect():
            return 0

        db.cursor.execute("SELECT COUNT(*) FROM students")

        result = db.cursor.fetchone()

        return result[0]

    except:
        return 0

    finally:
        db.close_connection()