"""
gui.py
------
All Tkinter screens for the Student Management System:
- LoginScreen   : admin authentication
- Dashboard     : main window with student table, form, search, buttons

Calls into auth.py (login) and student.py (CRUD) — contains no SQL itself.
"""

import tkinter as tk
from tkinter import ttk

from auth import login
from student import (
    add_student,
    update_student,
    delete_student,
    get_all_students,
    search_students,
    get_total_student_count,
)
from utils import (
    is_valid_email,
    is_valid_phone,
    is_not_empty,
    is_valid_age,
    show_error,
    show_success,
    ask_confirmation,
)
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT, DEPARTMENTS, GENDERS


class LoginScreen(tk.Tk):
    """First screen shown: asks for admin username/password."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} - Login")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")
        self._build_widgets()

    def _build_widgets(self):
        tk.Label(
            self, text="Admin Login", font=("Segoe UI", 20, "bold"),
            bg="#f0f2f5", fg="#1a1a2e"
        ).pack(pady=(40, 20))

        form = tk.Frame(self, bg="#f0f2f5")
        form.pack()

        tk.Label(form, text="Username", bg="#f0f2f5").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(form, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Password", bg="#f0f2f5").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(form, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        self.password_entry.bind("<Return>", lambda event: self._handle_login())

        tk.Button(
            self, text="Login", width=20, bg="#4361ee", fg="white",
            command=self._handle_login
        ).pack(pady=25)

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not is_not_empty(username) or not is_not_empty(password):
            show_error("Login Failed", "Username and password are required.")
            return

        if login(username, password):
            self.destroy()
            app = Dashboard()
            app.mainloop()
        else:
            show_error("Login Failed", "Invalid username or password.")


class Dashboard(tk.Tk):
    """Main application window: student table, form, search, and actions."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} - Dashboard")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.selected_student_id = None  # tracks which row is selected for update/delete

        self._build_layout()
        self._refresh_table()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        # --- Top bar: title + logout ---
        top_bar = tk.Frame(self, bg="#1a1a2e", height=50)
        top_bar.pack(fill="x")
        tk.Label(
            top_bar, text=APP_TITLE, font=("Segoe UI", 14, "bold"),
            bg="#1a1a2e", fg="white"
        ).pack(side="left", padx=15, pady=10)
        tk.Button(
            top_bar, text="Logout", bg="#e63946", fg="white",
            command=self._logout
        ).pack(side="right", padx=15, pady=10)

        # --- Student form ---
        form_frame = tk.LabelFrame(self, text="Student Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=15, pady=10)

        self.entries = {}
        fields = [
            ("Full Name", "name"),
            ("Age", "age"),
            ("Email", "email"),
            ("Phone Number", "phone"),
        ]
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=0, column=i * 2, sticky="w", padx=5)
            entry = tk.Entry(form_frame, width=20)
            entry.grid(row=0, column=i * 2 + 1, padx=5, pady=5)
            self.entries[key] = entry

        tk.Label(form_frame, text="Gender").grid(row=1, column=0, sticky="w", padx=5)
        self.gender_var = tk.StringVar(value=GENDERS[0])
        ttk.Combobox(
            form_frame, textvariable=self.gender_var, values=GENDERS,
            state="readonly", width=18
        ).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Department").grid(row=1, column=2, sticky="w", padx=5)
        self.department_var = tk.StringVar(value=DEPARTMENTS[0])
        ttk.Combobox(
            form_frame, textvariable=self.department_var, values=DEPARTMENTS,
            state="readonly", width=18
        ).grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Address").grid(row=2, column=0, sticky="w", padx=5)
        self.address_entry = tk.Entry(form_frame, width=60)
        self.address_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # --- Action buttons ---
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(button_frame, text="Add Student", bg="#2a9d8f", fg="white",
                  width=14, command=self._handle_add).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Student", bg="#457b9d", fg="white",
                  width=14, command=self._handle_update).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Student", bg="#e63946", fg="white",
                  width=14, command=self._handle_delete).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Clear Form", width=14,
                  command=self._clear_form).grid(row=0, column=3, padx=5)

        # --- Search bar ---
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(search_frame, text="Search (name or ID):").pack(side="left", padx=(0, 5))
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)

        tk.Label(search_frame, text="Department:").pack(side="left", padx=(15, 5))
        self.filter_department_var = tk.StringVar(value="All")
        ttk.Combobox(
            search_frame, textvariable=self.filter_department_var,
            values=["All"] + DEPARTMENTS, state="readonly", width=18
        ).pack(side="left", padx=5)

        tk.Button(search_frame, text="Search", command=self._handle_search).pack(side="left", padx=10)
        tk.Button(search_frame, text="Show All", command=self._refresh_table).pack(side="left", padx=5)

        self.count_label = tk.Label(search_frame, text="Total Students: 0", font=("Segoe UI", 10, "bold"))
        self.count_label.pack(side="right", padx=10)

        # --- Student table ---
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("id", "name", "age", "gender", "course", "email", "phone", "address")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = ["ID", "Name", "Age", "Gender", "Department", "Email", "Phone", "Address"]
        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=110, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _refresh_table(self, rows=None):
        """Reloads the table. If rows is None, fetches all students."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = rows if rows is not None else get_all_students()
        for student in data:
            self.tree.insert("", "end", values=student)

        self.count_label.config(text=f"Total Students: {get_total_student_count()}")

    def _on_row_select(self, event):
        """When a table row is clicked, load its data into the form."""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_student_id = values[0]

        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, values[1])
        self.entries["age"].delete(0, tk.END)
        self.entries["age"].insert(0, values[2])
        self.gender_var.set(values[3])
        self.department_var.set(values[4])
        self.entries["email"].delete(0, tk.END)
        self.entries["email"].insert(0, values[5])
        self.entries["phone"].delete(0, tk.END)
        self.entries["phone"].insert(0, values[6])
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, values[7])

    def _clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.gender_var.set(GENDERS[0])
        self.department_var.set(DEPARTMENTS[0])
        self.selected_student_id = None
        self.tree.selection_remove(self.tree.selection())

    def _get_form_data(self):
        return {
            "name": self.entries["name"].get().strip(),
            "age": self.entries["age"].get().strip(),
            "gender": self.gender_var.get(),
            "course": self.department_var.get(),
            "email": self.entries["email"].get().strip(),
            "phone": self.entries["phone"].get().strip(),
            "address": self.address_entry.get().strip(),
        }

    def _validate_form(self, data):
        """Runs all field validations. Returns (True, "") or (False, error_message)."""
        if not all(is_not_empty(v) for k, v in data.items() if k != "address"):
            return False, "All fields except Address are required."
        if not is_valid_age(data["age"]):
            return False, "Age must be a whole number between 1 and 120."
        if not is_valid_email(data["email"]):
            return False, "Please enter a valid email address."
        if not is_valid_phone(data["phone"]):
            return False, "Phone number must be 10-15 digits (optional + prefix)."
        return True, ""

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def _handle_add(self):
        data = self._get_form_data()
        is_valid, message = self._validate_form(data)
        if not is_valid:
            show_error("Validation Error", message)
            return

        success, message = add_student(
            data["name"], int(data["age"]), data["gender"], data["course"],
            data["email"], data["phone"], data["address"]
        )
        if success:
            show_success("Success", message)
            self._clear_form()
            self._refresh_table()
        else:
            show_error("Error", message)

    def _handle_update(self):
        if not self.selected_student_id:
            show_error("No Selection", "Please select a student from the table to update.")
            return

        data = self._get_form_data()
        is_valid, message = self._validate_form(data)
        if not is_valid:
            show_error("Validation Error", message)
            return

        success, message = update_student(
            self.selected_student_id, data["name"], int(data["age"]), data["gender"],
            data["course"], data["email"], data["phone"], data["address"]
        )
        if success:
            show_success("Success", message)
            self._clear_form()
            self._refresh_table()
        else:
            show_error("Error", message)

    def _handle_delete(self):
        if not self.selected_student_id:
            show_error("No Selection", "Please select a student from the table to delete.")
            return

        if not ask_confirmation("Confirm Delete", "Are you sure you want to delete this student?"):
            return

        success, message = delete_student(self.selected_student_id)
        if success:
            show_success("Success", message)
            self._clear_form()
            self._refresh_table()
        else:
            show_error("Error", message)

    def _handle_search(self):
        keyword = self.search_entry.get().strip() or None
        department = self.filter_department_var.get()
        department = None if department == "All" else department

        results = search_students(keyword=keyword, department=department)
        self._refresh_table(rows=results)

    def _logout(self):
        if ask_confirmation("Logout", "Are you sure you want to logout?"):
            self.destroy()
            login_screen = LoginScreen()
            login_screen.mainloop()


def run_app():
    """Entry point used by main.py to start the application."""
    app = LoginScreen()
    app.mainloop()