from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "9487")
DB_NAME     = os.getenv("DB_NAME", "pdf_summary")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── 테이블 모델 ──
class PdfDocument(Base):
    __tablename__ = "pdf_documents"

    id             = Column(Integer, primary_key=True, index=True)
    filename       = Column(String(255), nullable=False)
    extracted_text = Column(Text)  # LONGTEXT 대신 일반 Text나 대소문자 확인
    summary        = Column(Text)
    model_used     = Column(String(100))
    char_count     = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.datetime.now)

    # ⚠️ 이 부분들이 없어서 에러가 났던 것입니다. 추가해 주세요!
    file_size_bytes         = Column(Integer) 
    extraction_time_seconds = Column(Numeric(10, 3))

# ── DB 세션 의존성 ──
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── 테이블 자동 생성 ──
def init_db():
    Base.metadata.create_all(bind=engine)