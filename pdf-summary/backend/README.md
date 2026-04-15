# PDF Summary Backend

FastAPI 기반 백엔드 서비스입니다.
문서 업로드부터 OCR, 요약/번역, 인증/세션, 관리자 API, 결제, WebSocket, 비동기 작업을 담당합니다.

## 1. 핵심 역할

- 인증/세션: 로그인, 회원가입, 소셜 로그인, 세션 검증/강제 종료
- 문서 처리: 추출, 요약, 번역, 문서 CRUD, 다운로드
- 관리자 기능: 사용자/문서 관리, 시스템 상태, 결제 로그, 활성 세션 조회
- 결제 기능: KakaoPay ready/approve 처리 및 결제 이력 저장
- 실시간 기능: Socket.IO 기반 대화형 이벤트 처리
- 비동기 처리: Celery + Redis 큐로 OCR/LLM 작업 분리

## 2. 최근 반영 사항 (2026-04)

### 관리자 회원 삭제 안정성 강화

- 회원 삭제 시 FK 충돌을 줄이기 위해 결제 이력 선삭제 조건을 강화했습니다.
- 삭제 대상:
  - payment_transactions.user_id == 대상 사용자
  - 또는 payment_transactions.document_id가 대상 사용자의 문서인 경우
- 위 정리 후 pdf_documents를 삭제하도록 순서를 보강했습니다.

### 프로필/탈퇴 정책 관련

- 프로필 수정 API는 이메일 변경 엔드포인트를 유지하지만, 현재 프론트 UI에서는 이메일 변경을 차단합니다.
- 회원 탈퇴는 withdraw API를 통해 문서/세션/로그/결제 이력을 정리 후 계정을 삭제합니다.

## 3. 디렉토리 구조

```text
backend/
├── main.py
├── websocket_main.py
├── celery_app.py
├── database.py
├── database_migration.sql
├── database_migration_category_official.sql
├── migrate_database.py
├── reset_password.py
├── test_password.py
├── requirements.txt
├── routers/
│   ├── auth/          # register, login, profile, find_account, sessions, social
│   ├── admin/         # users, documents, system
│   ├── document/      # crud, summarize, translate, utility, download
│   ├── payment/       # kakao
│   └── websocket/     # socket 이벤트/서비스
├── services/
│   ├── ai_service.py
│   ├── ai_service_chat.py
│   ├── ai_service_extract.py
│   ├── pdf_service.py
│   └── ocr/
├── tasks/
│   └── document_tasks.py
├── templates/
│   └── email_template.html
└── utils/
    ├── auth_utils.py
    ├── discord.py
    └── email_utils.py
```

## 4. 실행 방법

### 4-1. 로컬 실행

```bash
cd pdf-summary/backend
pip install -r requirements.txt
mysql -u root -p pdf_summary < database_migration.sql
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

별도 터미널:

```bash
cd pdf-summary/backend
python websocket_main.py

python -m celery -A celery_app.celery_app worker -Q ocr --loglevel=info --concurrency=1
python -m celery -A celery_app.celery_app worker -Q llm --loglevel=info --concurrency=2
python -m celery -A celery_app.celery_app flower --port=5555
```

### 4-2. Docker 실행

```bash
cd pdf-summary

# 기본 실행 (외부/로컬 Ollama 사용)
docker compose up --build

# Ollama 포함 실행
docker compose --profile ollama up --build
```

## 5. 서비스 포트

| 서비스 | 포트 | 비고 |
| --- | --- | --- |
| FastAPI | 8000 | REST API, OpenAPI |
| WebSocket | 8001 | Socket.IO |
| MariaDB | 3307 | 컨테이너 내부 3306 |
| Redis | 6379 | 브로커/백엔드 |
| ChromaDB | 8002 | 컨테이너 내부 8000 |
| Flower | 5555 | Celery 모니터링 |

## 6. 라우터 구성

| Prefix | 설명 |
| --- | --- |
| /auth | 인증, 세션, 프로필, 회원탈퇴 |
| /api/documents | 문서 CRUD, 추출, 요약, 번역, 다운로드 |
| /api/admin | 사용자/문서/시스템/결제 로그 |
| /api/payments | KakaoPay ready/approve |
| /socket.io | Socket.IO 앱 마운트 |

## 7. 주요 엔드포인트

### 인증/세션

```text
POST   /auth/login
POST   /auth/register
POST   /auth/logout
GET    /auth/sessions/validate
GET    /auth/sessions/current
DELETE /auth/sessions/{session_id}
POST   /auth/find-account
GET    /auth/social/kakao/login
GET    /auth/social/kakao/callback
GET    /auth/profile/{user_db_id}
PUT    /auth/profile/{user_db_id}
DELETE /auth/withdraw/{username}
```

### 문서

```text
POST   /api/documents/extract
POST   /api/documents/summarize-document
POST   /api/documents/translate
GET    /api/documents/documents/{document_id}
GET    /api/documents/users/{user_id}/documents
PATCH  /api/documents/documents/{document_id}/public
POST   /api/documents/download-selected
GET    /api/documents/models
GET    /api/documents/ocr-models
```

### 관리자

```text
GET    /api/admin/users
DELETE /api/admin/users/{user_id}
GET    /api/admin/documents
PUT    /api/admin/documents/{document_id}
DELETE /api/admin/documents/{document_id}
GET    /api/admin/documents/payment-logs
GET    /api/admin/database-status
GET    /api/admin/chroma-status
GET    /api/admin/active-sessions
```

### 결제

```text
POST   /api/payments/kakao/ready
POST   /api/payments/kakao/approve
```

## 8. 환경 변수

파일 위치: backend/.env

```env
# DB
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pdf_summary

# CORS
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# AI / RAG
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
EXTRACT_DEFAULT_MODEL=gemma3:latest
CHAT_DEFAULT_MODEL=exaone3.5:2.4b
CHAT_NUM_CTX=4096
CHAT_NUM_PREDICT=900
CHAT_REPEAT_PENALTY=1.1
CHROMA_BASE_URL=http://localhost:8000
CHROMA_COLLECTION=documents

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# OCR
OCR_USE_GPU=true
PADDLE_DEVICE=gpu:0
PADDLE_DET_DB_THRESH=0.3
PADDLE_DET_DB_BOX_THRESH=0.6
PADDLE_DET_DB_UNCLIP_RATIO=1.5
PADDLE_DET_DB_SCORE_MODE=fast
PADDLE_DET_LIMIT_SIDE_LEN=960
PADDLE_CUSTOM_MODEL_DIR=/app/paddletrain
TESSDATA_PREFIX=/tessdata
LIBREOFFICE_PATH=/usr/bin/soffice

# KakaoPay
KAKAO_PAY_SECRET_KEY=YOUR_SECRET_KEY
KAKAO_PAY_CID=TC0ONETIME
FRONTEND_BASE_URL=http://localhost:5173

# Kakao 소셜 로그인
KAKAO_CLIENT_ID=YOUR_KAKAO_REST_API_KEY
KAKAO_REDIRECT_URI=http://localhost:5173/auth/kakao/callback

# Discord 알림
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## 9. 데이터 모델 요약

- users: 사용자 기본 정보
- user_sessions: 로그인 세션
- pdf_documents: 문서 메타/본문/요약/번역
- admin_activity_logs: 관리자 활동 이력
- payment_transactions: 결제 이력

운영 시 FK 관련 삭제 순서를 보장해야 하며, 특히 users와 pdf_documents를 삭제할 때 payment_transactions 선정리가 중요합니다.

## 10. 운영 체크포인트

- CORS + 500 동시 발생 시 preflight(OPTIONS)와 서버 예외를 함께 확인합니다.
- PaddleOCR GPU 불안정 시 OCR_USE_GPU=false로 CPU 폴백을 적용합니다.
- 결제/소셜 Kakao 키는 서로 다른 키 체계를 사용합니다.
- 테이블 자동 생성(Base.metadata.create_all)은 개발 편의용이며, 운영은 migration SQL 기준 관리를 권장합니다.
