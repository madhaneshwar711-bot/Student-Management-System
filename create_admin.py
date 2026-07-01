from auth import create_admin

username = "admin"
password = "admin123"

if create_admin(username, password):
    print("Admin created successfully!")
else:
    print("Failed to create admin.")