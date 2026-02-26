from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT, DECIMAL  # ← 여기 추가!
from sqlalchemy import BigInteger   # ← 여기 추가!
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
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_NAME     = os.getenv("DB_NAME", "pdf_summary")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── 테이블 모델 ──
class PdfDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    extracted_text = Column(LONGTEXT)
    summary = Column(LONGTEXT)
    model_used = Column(String(100))
    char_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # [재훈] 2026-02-26 
    # 컬럼 추가
    original_translation = Column(LONGTEXT)
    summary_translation = Column(LONGTEXT)
    translation_model = Column(String(100))
    extraction_time_seconds = Column(DECIMAL(10, 3))
    summary_time_seconds = Column(DECIMAL(10, 3))
    translation_time_seconds = Column(DECIMAL(10, 3))
    file_size_bytes = Column(BigInteger)
    total_pages = Column(Integer)
    successful_pages = Column(Integer)


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