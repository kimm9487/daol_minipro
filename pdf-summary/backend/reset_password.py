import bcrypt
from database import SessionLocal, User

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

db = SessionLocal()

# admin 계정 업데이트
admin_user = db.query(User).filter(User.username == "admin").first()
if admin_user:
    print(f"Before - Password hash: {admin_user.password_hash}")
    
    # admin123 비밀번호로 업데이트
    admin_user.password_hash = hash_password("admin123")
    db.commit()
    
    print(f"After - Password hash: {admin_user.password_hash}")
    print("✅ Admin password updated successfully!")
    
    # 검증
    from database import User as UserModel
    admin_verify = db.query(UserModel).filter(UserModel.username == "admin").first()
    is_valid = bcrypt.checkpw("admin123".encode('utf-8'), admin_verify.password_hash.encode('utf-8'))
    print(f"Password verification test: {is_valid}")
else:
    print("❌ Admin user not found!")

db.close()
