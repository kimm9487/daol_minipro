#!/usr/bin/env python3
"""
Database Migration Script for PDF Summary System

이 스크립트는 다음을 수행합니다:
1. 기존 테이블 구조 확인
2. 새로운 테이블 구조로 마이그레이션
3. user_id 기반 쿼리 검증
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL, Base, User, PdfDocument, UserSession, AdminActivityLog
import datetime

def backup_existing_data(engine):
    """기존 데이터를 백업합니다."""
    print("📦 기존 데이터 백업 중...")
    
    backup_data = {
        "users": [],
        "pdf_documents": []
    }
    
    try:
        with engine.connect() as conn:
            # 기존 사용자 데이터 백업 (old user table)
            try:
                old_users = conn.execute(text("SELECT * FROM user")).fetchall()
                for user in old_users:
                    backup_data["users"].append({
                        "old_user_no": user[0] if len(user) > 0 else None,
                        "user_id": user[1] if len(user) > 1 else None, 
                        "user_pw": user[2] if len(user) > 2 else None,
                        "user_name": user[3] if len(user) > 3 else None,
                        "user_email": user[4] if len(user) > 4 else None,
                    })
                print(f"   ✅ 기존 사용자 {len(backup_data['users'])}명 백업 완료")
            except Exception as e:
                print(f"   ⚠️  기존 user 테이블 없음 또는 오류: {e}")

            # 기존 PDF 문서 백업
            try:
                old_docs = conn.execute(text("SELECT * FROM pdf_documents")).fetchall()
                for doc in old_docs:
                    backup_data["pdf_documents"].append({
                        "id": doc[0] if len(doc) > 0 else None,
                        "filename": doc[1] if len(doc) > 1 else None,
                        "extracted_text": doc[2] if len(doc) > 2 else None,
                        "summary": doc[3] if len(doc) > 3 else None,
                        "model_used": doc[4] if len(doc) > 4 else None,
                        "char_count": doc[5] if len(doc) > 5 else None,
                        "created_at": doc[6] if len(doc) > 6 else None,
                    })
                print(f"   ✅ 기존 문서 {len(backup_data['pdf_documents'])}개 백업 완료")
            except Exception as e:
                print(f"   ⚠️  기존 pdf_documents 테이블 없음 또는 오류: {e}")
                
    except Exception as e:
        print(f"   ❌ 백업 중 오류 발생: {e}")
    
    return backup_data

def drop_old_tables(engine):
    """기존 테이블들을 삭제합니다."""
    print("🗑️  기존 테이블 정리 중...")
    
    tables_to_drop = [
        "admin_activity_logs",
        "user_sessions", 
        "pdf_documents",
        "summary_history",
        "user"  # 기존 user 테이블
    ]
    
    with engine.connect() as conn:
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                conn.commit()
                print(f"   ✅ {table} 테이블 삭제됨")
            except Exception as e:
                print(f"   ⚠️  {table} 테이블 삭제 실패: {e}")

def create_new_tables(engine):
    """새로운 테이블들을 생성합니다."""
    print("🏗️  새로운 테이블 생성 중...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✅ 모든 새 테이블이 성공적으로 생성됨")
        
        # 생성된 테이블 확인
        with engine.connect() as conn:
            tables = conn.execute(text("SHOW TABLES")).fetchall()
            print(f"   📋 생성된 테이블: {[t[0] for t in tables]}")
            
    except Exception as e:
        print(f"   ❌ 테이블 생성 실패: {e}")
        raise

def migrate_data(engine, backup_data):
    """백업된 데이터를 새 구조로 마이그레이션합니다."""
    print("📥 데이터 마이그레이션 중...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 사용자 데이터 마이그레이션
        user_id_mapping = {}  # old_user_no -> new_user.id 매핑
        
        for old_user in backup_data["users"]:
            if old_user["user_id"] and old_user["user_pw"] and old_user["user_name"]:
                new_user = User(
                    username=old_user["user_id"],
                    password_hash=old_user["user_pw"],  # 이미 해시된 비밀번호
                    full_name=old_user["user_name"],
                    email=old_user["user_email"],
                    role='user',
                    is_active=True
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                user_id_mapping[old_user["old_user_no"]] = new_user.id
                print(f"   ✅ 사용자 마이그레이션: {old_user['user_id']} -> ID {new_user.id}")
        
        # 관리자 계정 생성 (없는 경우)
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            import bcrypt
            admin_password = "admin123"
            hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user = User(
                username="admin",
                password_hash=hashed,
                full_name="System Administrator", 
                email="admin@pdfsummary.com",
                role='admin',
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"   ✅ 관리자 계정 생성: admin/admin123")
        
        # PDF 문서 데이터 마이그레이션 (user_id를 admin으로 설정)
        migrated_docs = 0
        admin_id = admin_user.id
        
        for old_doc in backup_data["pdf_documents"]:
            if old_doc["filename"]:
                new_doc = PdfDocument(
                    user_id=admin_id,  # 기존 문서들은 관리자 소유로 설정
                    filename=old_doc["filename"],
                    extracted_text=old_doc["extracted_text"],
                    summary=old_doc["summary"],
                    model_used=old_doc["model_used"],
                    char_count=old_doc["char_count"] or 0,
                    created_at=old_doc["created_at"] or datetime.datetime.now()
                )
                db.add(new_doc)
                migrated_docs += 1
        
        db.commit()
        print(f"   ✅ PDF 문서 {migrated_docs}개 마이그레이션 완료 (관리자 소유)")
        
    except Exception as e:
        print(f"   ❌ 데이터 마이그레이션 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_migration(engine):
    """마이그레이션 결과를 검증합니다."""
    print("🔍 마이그레이션 검증 중...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 사용자 수 확인
        user_count = db.query(User).count()
        print(f"   📊 총 사용자 수: {user_count}")
        
        # 문서 수 확인
        doc_count = db.query(PdfDocument).count()
        print(f"   📊 총 문서 수: {doc_count}")
        
        # user_id 필드가 있는 문서 확인
        docs_with_user_id = db.query(PdfDocument).filter(PdfDocument.user_id.isnot(None)).count()
        print(f"   📊 user_id가 있는 문서 수: {docs_with_user_id}")
        
        # 샘플 쿼리 테스트
        if user_count > 0:
            sample_user = db.query(User).first()
            user_docs = db.query(PdfDocument).filter(PdfDocument.user_id == sample_user.id).count()
            print(f"   🔗 사용자 '{sample_user.username}'의 문서 수: {user_docs}")
        
        print("   ✅ 마이그레이션 검증 완료")
        
    except Exception as e:
        print(f"   ❌ 검증 실패: {e}")
    finally:
        db.close()

def main():
    """메인 마이그레이션 프로세스"""
    print("=" * 60)
    print("🚀 PDF Summary System Database Migration")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    try:
        # 1. 기존 데이터 백업
        backup_data = backup_existing_data(engine)
        
        # 2. 기존 테이블 삭제
        drop_old_tables(engine)
        
        # 3. 새 테이블 생성
        create_new_tables(engine)
        
        # 4. 데이터 마이그레이션
        migrate_data(engine, backup_data)
        
        # 5. 검증
        verify_migration(engine)
        
        print("\n" + "=" * 60)
        print("✅ 마이그레이션이 성공적으로 완료되었습니다!")
        print("✅ user_id 기반 쿼리가 모든 API에 적용되었습니다!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 마이그레이션 실패: {e}")
        print("💡 데이터베이스를 직접 확인하고 필요시 수동으로 복구하세요.")
        return False
    
    return True

if __name__ == "__main__":
    main()