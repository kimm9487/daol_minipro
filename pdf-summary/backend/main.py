"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import summary
from database import init_db

app = FastAPI(title="PDF 문서 요약 시스템", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()  # 데이터베이스 초기화 (테이블 생성)

# 라우터 등록
app.include_router(summary.router, prefix="/api", tags=["summary"])


@app.get("/")
def root():
    return {"message": "PDF 요약 시스템 API 서버 실행 중"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
import os
import bcrypt
from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 1. DB 설정
DB_URL = "mysql+pymysql://root:9487@localhost:3306/pdf_summary"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DB 모델
class Member(Base):
    __tablename__ = "members"
    user_no = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False)
    user_pw = Column(String(255), nullable=False)
    user_name = Column(String(50), nullable=False)
    user_email = Column(String(100))

Base.metadata.create_all(bind=engine)

# 3. FastAPI 설정
app = FastAPI(title="PDF 요약 시스템 API")

# ⚠️ 중요: CORS 설정 (React 기본 포트 5173 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. 비밀번호 암호화/확인 함수
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 5. API 엔드포인트: 회원가입 (React 연결을 위해 JSON 응답으로 변경)
@app.post("/auth/register")
def register(
    user_id: str = Form(...), 
    user_pw: str = Form(...), 
    user_name: str = Form(...), 
    user_email: str = Form(None),
    db: Session = Depends(get_db)
):
    existing = db.query(Member).filter(Member.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    
    hashed_pw = hash_password(user_pw)
    new_user = Member(user_id=user_id, user_pw=hashed_pw, user_name=user_name, user_email=user_email)
    db.add(new_user)
    db.commit()
    
    # ⚠️ React에서는 리다이렉트 대신 JSON 메시지를 보내 프론트에서 처리하게 합니다.
    return {"message": "회원가입이 완료되었습니다."}

# 6. API 엔드포인트: 로그인
@app.post("/auth/login")
def login(user_id: str = Form(...), user_pw: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Member).filter(Member.user_id == user_id).first()
    
    if not user or not verify_password(user_pw, user.user_pw):
        # ⚠️ 에러 발생 시 HTTP 상태 코드 401을 반환
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")
    
    return {
        "message": "로그인 성공",
        "user_name": user.user_name,
        "user_id": user.user_id
    }

@app.get("/auth/check-id")
def check_id(user_id: str, db: Session = Depends(get_db)):
    # DB에서 해당 아이디가 있는지 조회
    user = db.query(Member).filter(Member.user_id == user_id).first()
    
    if user:
        # 중복된 아이디가 있는 경우 (400 에러 또는 별도 메시지)
        return {"available": False, "message": "이미 사용 중인 아이디입니다."}
    
    return {"available": True, "message": "사용 가능한 아이디입니다."}

# 7. (선택사항) 정적 파일 연결 해제
# React는 별도의 서버(Vite)에서 돌아가므로 app.mount("/") 부분은 더 이상 필요 없습니다.
# 나중에 배포(Build)할 때만 다시 연결하면 됩니다.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)