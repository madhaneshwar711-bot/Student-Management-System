# utils.py

import re
from tkinter import messagebox


# -----------------------------
# VALIDATION FUNCTIONS
# -----------------------------

def is_valid_email(email):
    """
    Validate email format.
    """
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone):
    """
    Validates phone number (10-15 digits, optional +).
    """
    pattern = r"^\+?\d{10,15}$"
    return bool(re.match(pattern, phone))


def is_not_empty(value):
    """
    Checks if a field is not blank.
    """
    return bool(str(value).strip())


def is_valid_age(age):
    """
    Age must be between 1 and 120.
    """
    try:
        age = int(age)
        return 1 <= age <= 120
    except:
        return False


# -----------------------------
# MESSAGE BOX HELPERS
# -----------------------------

def show_error(title, message):
    messagebox.showerror(title, message)


def show_success(title, message):
    messagebox.showinfo(title, message)


def show_info(title, message):
    messagebox.showinfo(title, message)


def ask_confirmation(title, message):
    """
    Returns True if user clicks Yes.
    """
    return messagebox.askyesno(title, message)