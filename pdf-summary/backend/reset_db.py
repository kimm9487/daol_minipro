#!/usr/bin/env python3
"""
Simple Database Reset Script
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from database import init_db, engine, Base
    from sqlalchemy import text
    
    print("🚀 데이터베이스 테이블 재생성 시작...")
    
    # 1. 기존 테이블 삭제
    print("🗑️  기존 테이블 삭제 중...")
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS admin_activity_logs"))
            conn.execute(text("DROP TABLE IF EXISTS user_sessions"))
            conn.execute(text("DROP TABLE IF EXISTS pdf_documents"))
            conn.execute(text("DROP TABLE IF EXISTS summary_history"))
            conn.execute(text("DROP TABLE IF EXISTS user"))
            conn.execute(text("DROP TABLE IF EXISTS users"))
            conn.commit()
            print("   ✅ 기존 테이블 삭제 완료")
        except Exception as e:
            print(f"   ⚠️  테이블 삭제 중 오류 (무시됨): {e}")
    
    # 2. 새 테이블 생성
    print("🏗️  새 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    
    # 3. 테이블 확인
    print("📋 생성된 테이블 확인 중...")
    with engine.connect() as conn:
        tables = conn.execute(text("SHOW TABLES")).fetchall()
        for table in tables:
            print(f"   ✅ {table[0]}")
    
    print("\n✅ 데이터베이스 재생성 완료!")
    print("✅ PdfDocument 클래스 중복 제거됨")
    print("✅ user_id 기반 쿼리 구조 적용됨")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()