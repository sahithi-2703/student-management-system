import mysql.connector
from mysql.connector import Error

import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": "student_db",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def run_query(query, params=None, fetch=False):
    """Runs a query safely. Returns rows if fetch=True."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.rowcount
    except Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()


def print_students(rows):
    if not rows:
        print("No students found.")
        return
    print(f"\n{'ID':<5}{'Name':<22}{'Age':<6}{'Course':<18}{'Email':<26}{'Phone'}")
    print("-" * 85)
    for r in rows:
        print(f"{r[0]:<5}{r[1]:<22}{str(r[2]):<6}{str(r[3]):<18}{str(r[4]):<26}{r[5]}")


def add_student():
    name = input("Name: ").strip()
    if not name:
        print("Name is required.")
        return
    age = input("Age: ").strip()
    course = input("Course: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()

    result = run_query(
        "INSERT INTO students (name, age, course, email, phone) VALUES (%s, %s, %s, %s, %s)",
        (name, int(age) if age.isdigit() else None, course, email or None, phone),
    )
    if result:
        print("Student added!")


def view_students():
    rows = run_query(
        "SELECT id, name, age, course, email, phone FROM students ORDER BY id",
        fetch=True,
    )
    print_students(rows)


def search_student():
    keyword = input("Search by name or course: ").strip()
    rows = run_query(
        "SELECT id, name, age, course, email, phone FROM students "
        "WHERE name LIKE %s OR course LIKE %s",
        (f"%{keyword}%", f"%{keyword}%"),
        fetch=True,
    )
    print_students(rows)


def update_student():
    sid = input("Student ID to update: ").strip()
    if not sid.isdigit():
        print("Invalid ID.")
        return
    print("Leave blank to keep the current value.")
    name = input("New name: ").strip()
    age = input("New age: ").strip()
    course = input("New course: ").strip()
    email = input("New email: ").strip()
    phone = input("New phone: ").strip()

    fields, values = [], []
    for col, val in [("name", name), ("age", age), ("course", course),
                     ("email", email), ("phone", phone)]:
        if val:
            fields.append(f"{col} = %s")
            values.append(int(val) if col == "age" and val.isdigit() else val)

    if not fields:
        print("Nothing to update.")
        return

    values.append(int(sid))
    result = run_query(f"UPDATE students SET {', '.join(fields)} WHERE id = %s", values)
    print("Updated!" if result else "No student with that ID.")


def delete_student():
    sid = input("Student ID to delete: ").strip()
    if not sid.isdigit():
        print("Invalid ID.")
        return
    if input("Are you sure? (y/n): ").lower() != "y":
        print("Cancelled.")
        return
    result = run_query("DELETE FROM students WHERE id = %s", (int(sid),))
    print("Deleted!" if result else "No student with that ID.")


def main():
    actions = {
        "1": add_student,
        "2": view_students,
        "3": search_student,
        "4": update_student,
        "5": delete_student,
    }
    while True:
        print("\n=== Student Management System ===")
        print("1. Add student")
        print("2. View all students")
        print("3. Search student")
        print("4. Update student")
        print("5. Delete student")
        print("6. Exit")
        choice = input("Choose: ").strip()
        if choice == "6":
            print("Bye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
