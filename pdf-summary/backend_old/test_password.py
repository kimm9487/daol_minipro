import bcrypt
from database import get_db, User

db = next(get_db())
admin_user = db.query(User).filter(User.username == "admin").first()

if admin_user:
    print(f"Admin user found: {admin_user.username}")
    print(f"Password hash: {admin_user.password_hash}")
    
    # Test password verification
    test_password = "admin123"
    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), admin_user.password_hash.encode('utf-8'))
    print(f"Password 'admin123' verification: {is_valid}")
else:
    print("Admin user not found!")

db.close()
