from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, DECIMAL, BigInteger
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
DB_NAME     = os.getenv("DB_NAME", "test")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── 확장된 테이블 모델 ──
class PdfDocument(Base):
    __tablename__ = "pdf_documents"

    # 기본 필드
    id             = Column(Integer, primary_key=True, index=True)
    filename       = Column(String(255), nullable=False)
    extracted_text = Column(LONGTEXT)
    summary        = Column(LONGTEXT)
    model_used     = Column(String(100))
    char_count     = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.datetime.now)
    
    # 번역 관련 필드 추가
    original_translation = Column(LONGTEXT, comment="원문 영문 번역")
    summary_translation = Column(LONGTEXT, comment="요약 영문 번역")
    translation_model = Column(String(100), comment="번역에 사용된 모델")
    
    # 처리 시간 추적 필드
    extraction_time_seconds = Column(DECIMAL(10,3), comment="텍스트 추출 소요 시간(초)")
    summary_time_seconds = Column(DECIMAL(10,3), comment="요약 생성 소요 시간(초)")
    translation_time_seconds = Column(DECIMAL(10,3), comment="번역 소요 시간(초)")
    
    # 파일 메타데이터 필드
    file_size_bytes = Column(BigInteger, comment="PDF 파일 크기(바이트)")
    total_pages = Column(Integer, comment="PDF 전체 페이지 수")
    successful_pages = Column(Integer, comment="성공적으로 추출된 페이지 수")


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