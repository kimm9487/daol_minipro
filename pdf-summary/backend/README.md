# PDF Summary Backend

FastAPI 기반 백엔드 서버입니다.
문서(PDF·HWP) 업로드·OCR·요약·번역, 세션 기반 인증, 관리자 API, WebSocket, KakaoPay 결제, Celery 비동기 큐, Discord 에러 알림을 제공합니다.

## 1. 주요 기능

- **인증/세션**: 로그인, 회원가입, 소셜 로그인(Kakao), 계정 찾기, 세션 목록·강제 종료
- **문서 처리**: 텍스트 추출, OCR(PaddleOCR·Tesseract·EasyOCR·Pororo·PyPDF2 팩토리), 요약, 번역, 문서 CRUD
- **HWP 지원**: LibreOffice + pyhwp를 통한 HWP → PDF 변환 후 처리
- **관리자 기능**: 사용자·문서 관리, DB 상태·Chroma 상태 조회, 결제 로그, 활성 세션 조회
- **결제**: 공개+중요 문서 대상 KakaoPay 결제 (ready/approve, 팝업 콜백)
- **비동기 작업**: Celery + Redis (OCR 큐·LLM 큐 분리)
- **실시간 기능**: python-socketio 기반 채팅/이벤트
- **알림**: Discord Webhook 에러·경고 알림

## 2. 디렉토리 구조

```text
backend/
├── main.py                                # FastAPI 앱 진입점, 라우터 등록
├── websocket_main.py                      # Socket.IO 서버 (포트 8001)
├── celery_app.py                          # Celery 앱 설정
├── database.py                            # SQLAlchemy 엔진·세션·모델 Base
├── database_migration.sql                 # 초기 스키마 마이그레이션
├── database_migration_category_official.sql # 카테고리 컬럼 마이그레이션
├── migrate_database.py                    # 마이그레이션 유틸리티 스크립트
├── reset_password.py                      # 비밀번호 초기화 유틸리티
├── test_password.py                       # 비밀번호 해시 검증 유틸리티
├── requirements.txt
├── routers/
│   ├── auth/
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── profile.py
│   │   ├── find_account.py
│   │   ├── sessions.py
│   │   └── social.py              # Kakao 소셜 로그인
│   ├── admin/
│   │   ├── users.py
│   │   ├── documents.py
│   │   └── system.py              # DB·Chroma 상태, 활성 세션
│   ├── document/
│   │   ├── crud.py
│   │   ├── summarize.py
│   │   ├── translate.py
│   │   ├── utility.py
│   │   └── download.py
│   ├── payment/
│   │   └── kakao.py
│   └── websocket/
│       ├── websocket.py
│       ├── websocket_events.py
│       ├── websocket_runtime.py
│       └── websocket_services.py
├── services/
│   ├── ai_service.py              # RAG 기반 문서 검색·응답
│   ├── ai_service_chat.py         # 대화형 채팅 서비스
│   ├── ai_service_extract.py      # Ollama 기반 텍스트 추출/요약
│   ├── pdf_service.py
│   └── ocr/                       # OCR 팩토리 패턴
│       ├── factory.py             # OCR 모델 선택 팩토리
│       ├── types.py
│       ├── image_preprocess.py
│       ├── markdown_layout.py
│       ├── pdf_page_renderer.py
│       ├── paddleocr_extractor.py # PaddleOCR (커스텀 모델 지원)
│       ├── tesseract_extractor.py
│       ├── easyocr_extractor.py
│       ├── pororo_extractor.py
│       └── pypdf2_extractor.py
├── tasks/
│   └── document_tasks.py          # Celery 비동기 작업 정의
├── templates/
│   └── email_template.html
└── utils/
    ├── auth_utils.py
    ├── discord.py                 # Discord Webhook 에러 알림
    └── email_utils.py
```

## 3. 실행 방법 (로컬)

### 3-1. 의존성 설치

```bash
cd pdf-summary/backend
pip install -r requirements.txt
```

> 권장: 루트의 `environment.yml` 기반 conda 환경 사용 (`conda activate tfod`)

### 3-2. DB 마이그레이션

```bash
# 초기 스키마
mysql -u root -p pdf_summary < database_migration.sql

# 카테고리 컬럼 추가 (선택)
mysql -u root -p pdf_summary < database_migration_category_official.sql

# 또는 Python 스크립트
python migrate_database.py
```

### 3-3. 서버 실행

```bash
# FastAPI (포트 8000)
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Socket.IO WebSocket (포트 8001)
python websocket_main.py

# Celery 워커 - OCR 큐
python -m celery -A celery_app.celery_app worker -Q ocr --loglevel=info --concurrency=1

# Celery 워커 - LLM 큐
python -m celery -A celery_app.celery_app worker -Q llm --loglevel=info --concurrency=2

# Flower 모니터링 (포트 5555)
python -m celery -A celery_app.celery_app flower --port=5555
```

접속:

- API: http://localhost:8000
- OpenAPI Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

## 4. 실행 방법 (Docker)

루트의 `pdf-summary/` 폴더에서 실행합니다.

```bash
# Ollama 없이 (로컬 Ollama 사용)
docker compose up --build

# Ollama 컨테이너 포함
docker compose --profile ollama up --build
```

Docker Compose 서비스 목록:

| 서비스 | 컨테이너 | 포트 |
| --- | --- | --- |
| db | pdf_db | 3307→3306 |
| redis | pdf_redis | 6379 |
| chroma | pdf_chroma | 8002→8000 |
| ollama (profile) | pdf_ollama | 11434 |
| backend | pdf_backend | 8000 |
| websocket | pdf_websocket | 8001 |
| worker_ocr | pdf_worker_ocr | - |
| worker_llm | pdf_worker_llm | - |
| flower | pdf_flower | 5555 |
| frontend | pdf_frontend | 5173 |

## 5. 라우터 구성

`main.py`에서 아래 라우터를 등록합니다.

| 접두사 | 포함 라우터 |
| --- | --- |
| /auth | register, login, profile, find_account, sessions, social |
| /api/admin | users, documents, system |
| /api/documents | crud, summarize, translate, utility, download |
| /api/payments | kakao (ready/approve) |
| /socket.io | websocket_app 마운트 |

## 6. 핵심 API

### 인증/세션

- POST /auth/login
- POST /auth/register
- POST /auth/logout
- GET /auth/sessions/validate
- GET /auth/sessions/current
- DELETE /auth/sessions/{session_id}

### 문서

Prefix: /api/documents

- POST /extract
- POST /summarize-document
- POST /translate
- GET /documents/{document_id}
- GET /users/{user_id}/documents
- PATCH /documents/{document_id}/public
- POST /download-selected
- GET /models
- GET /ocr-models

### 관리자

Prefix: /api/admin

- GET /documents
- PUT /documents/{document_id}
- DELETE /documents/{document_id}
- GET /documents/payment-logs
- GET /users
- DELETE /users/{user_id}
- GET /database-status
- GET /chroma-status

### 결제 (KakaoPay)

Prefix: /api/payments/kakao

- POST /ready
- POST /approve

결제 정책:

- 공개+중요 문서만 결제 대상
- 문서 소유자와 관리자는 결제 면제
- 결제 이력은 payment_transactions 테이블에 저장

## 7. 환경 변수

파일: backend/.env

### DB/공통

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pdf_summary

CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### AI/큐

```env
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_BASE_URL=http://localhost:8000
CHROMA_COLLECTION=documents
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### KakaoPay (결제 전용)

```env
KAKAO_PAY_SECRET_KEY=YOUR_SECRET_KEY
KAKAO_PAY_CID=TC0ONETIME
FRONTEND_BASE_URL=http://localhost:5173
```

중요:

- 결제 키(KAKAO_PAY_*)와 소셜 로그인 키(KAKAO_CLIENT_ID)는 별도입니다.
- 도메인 검증 오류가 나면 Kakao Developers에서 Web 플랫폼 사이트 도메인을 확인하세요.

## 8. 데이터베이스 테이블

핵심 테이블:

- users
- user_sessions
- pdf_documents
- admin_activity_logs
- payment_transactions

payment_transactions 주요 컬럼:

- document_id, user_id
- provider, status, amount
- partner_order_id, tid
- approved_at, created_at, updated_at

## 9. 개발 참고

- main.py에서 Base.metadata.create_all이 실행되어 모델 테이블을 자동 생성 시도합니다.
- 운영 환경에서는 database_migration.sql 기준으로 스키마를 관리하는 것을 권장합니다.
- CORS는 CORS_ALLOW_ORIGINS 미설정 시 localhost 기본값으로 동작합니다.
