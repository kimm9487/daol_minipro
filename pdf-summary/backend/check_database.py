"""
MariaDB 데이터베이스 상태 확인 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, PdfDocument, Base
from sqlalchemy import text, inspect
from datetime import datetime

def check_database_connection():
    """데이터베이스 연결 확인"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT VERSION()"))
        version = result.fetchone()[0]
        print(f"✅ 데이터베이스 연결 성공!")
        print(f"📊 MariaDB 버전: {version}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

def check_tables():
    """테이블 존재 확인"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 데이터베이스 테이블 목록:")
        for table in tables:
            print(f"  - {table}")
        
        if 'pdf_documents' in tables:
            print(f"✅ pdf_documents 테이블 존재함")
            return True
        else:
            print(f"⚠️ pdf_documents 테이블이 없음")
            return False
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {e}")
        return False

def check_table_structure():
    """pdf_documents 테이블 구조 확인"""
    try:
        db = SessionLocal()
        result = db.execute(text("DESCRIBE pdf_documents"))
        columns = result.fetchall()
        
        print(f"\n🏗️ pdf_documents 테이블 구조:")
        for col in columns:
            field, type_info, null, key, default, extra = col
            print(f"  {field:<25} {type_info:<20} {null:<5} {key:<5}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ 테이블 구조 확인 실패: {e}")
        return False

def check_data():
    """데이터 현황 확인"""
    try:
        db = SessionLocal()
        
        # 전체 문서 수
        total_count = db.query(PdfDocument).count()
        print(f"\n📊 데이터 현황:")
        print(f"  전체 문서 수: {total_count}")
        
        if total_count > 0:
            # 번역 완료된 문서 수
            original_translated = db.query(PdfDocument).filter(
                PdfDocument.original_translation.isnot(None)
            ).count()
            
            summary_translated = db.query(PdfDocument).filter(
                PdfDocument.summary_translation.isnot(None)
            ).count()
            
            print(f"  원문 번역 완료: {original_translated}")
            print(f"  요약 번역 완료: {summary_translated}")
            
            # 최근 문서들
            recent_docs = db.query(PdfDocument).order_by(
                PdfDocument.created_at.desc()
            ).limit(5).all()
            
            print(f"\n📝 최근 문서 5개:")
            for doc in recent_docs:
                created = doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else "시간 정보 없음"
                print(f"  ID:{doc.id} | {doc.filename} | {created}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")
        return False

def create_tables_if_needed():
    """필요시 테이블 생성"""
    try:
        print(f"\n🔧 테이블 생성 시도...")
        Base.metadata.create_all(bind=engine)
        print(f"✅ 테이블 생성/확인 완료")
        return True
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False

def main():
    print("=" * 60)
    print("📊 MariaDB 데이터베이스 상태 확인")
    print("=" * 60)
    
    # 1. 연결 확인
    if not check_database_connection():
        print("\n💡 해결방법:")
        print("  1. MariaDB 서버가 실행 중인지 확인")
        print("  2. .env 파일의 데이터베이스 설정 확인")
        print("  3. 데이터베이스 비밀번호 확인")
        return
    
    # 2. 테이블 확인 및 생성
    if not check_tables():
        print("\n🔧 테이블을 생성합니다...")
        if not create_tables_if_needed():
            return
        check_tables()
    
    # 3. 테이블 구조 확인
    check_table_structure()
    
    # 4. 데이터 현황 확인
    check_data()
    
    print("\n" + "=" * 60)
    print("✅ 데이터베이스 상태 확인 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()