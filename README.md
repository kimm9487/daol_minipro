# Daol Mini Project

PDF/문서(PDF·HWP) 업로드부터 OCR, AI 요약/번역, 대화형 질의응답, 관리자 운영, 결제 연동까지 포함한 통합 서비스입니다.

## 1. 문서 구성

- 루트 통합 문서: 이 파일
- 백엔드 상세 문서: pdf-summary/backend/README.md
- 프론트 상세 문서: pdf-summary/frontend/README.md

## 2. 전체 구조

```text
daol_minipro/
├── README.md
├── environment.yml
├── conda_packages.txt
├── conda_pip.txt
└── pdf-summary/
    ├── docker-compose.yml
    ├── backend/
    │   ├── README.md
    │   ├── main.py
    │   ├── websocket_main.py
    │   ├── celery_app.py
    │   ├── database.py
    │   ├── database_migration.sql
    │   ├── database_migration_category_official.sql
    │   ├── migrate_database.py
    │   ├── reset_password.py
    │   ├── requirements.txt
    │   ├── routers/
    │   │   ├── auth/          # 로그인·회원가입·세션·소셜·계정찾기
    │   │   ├── admin/         # 사용자·문서·시스템 관리
    │   │   ├── document/      # CRUD·추출·요약·번역·다운로드
    │   │   ├── payment/       # KakaoPay ready/approve
    │   │   └── websocket/     # Socket.IO 이벤트/런타임
    │   ├── services/
    │   │   ├── ai_service.py
    │   │   ├── ai_service_chat.py
    │   │   ├── ai_service_extract.py
    │   │   ├── pdf_service.py
    │   │   └── ocr/           # OCR 팩토리 (PaddleOCR·Tesseract·EasyOCR·Pororo·PyPDF2)
    │   ├── tasks/
    │   └── utils/             # auth_utils, discord, email_utils
    ├── frontend/
    │   ├── README.md
    │   ├── package.json
    │   ├── vite.config.js
    │   └── src/
    │       ├── components/    # Header, WebSocketChat, GuideChatbot
    │       ├── config/        # api.js
    │       ├── hooks/
    │       └── pages/         # HomeHub·PdfSummary·ChatSummary·MyPage·UserList·AdminDashboard·Login·Register·Payment
    ├── paddletrain/           # PaddleOCR 커스텀 파인튜닝 모델
    ├── tessdata/              # Tesseract 학습 데이터
    ├── db-backups/
    └── frontend_old/
```

## 3. 핵심 기능

- PDF·HWP 문서 업로드, OCR(PaddleOCR/Tesseract/EasyOCR/Pororo 선택), 요약, 번역
- 문서 기반 대화형 Q&A (Socket.IO + Ollama RAG)
- 공개/비공개, 중요문서 비밀번호, 다운로드(CSV/ZIP)
- 관리자 대시보드 (사용자·문서·시스템·결제 로그·활성 세션·Chroma 상태)
- KakaoPay 결제 연동 (공개+중요 문서, 팝업 콜백 방식)
- Discord Webhook 에러 알림

## 4. 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| Frontend | React 19, Vite 7, React Router DOM 7, socket.io-client 4, date-fns |
| Backend | FastAPI 0.115, Uvicorn, SQLAlchemy 2, python-socketio |
| Async | Celery 5 (OCR 큐·LLM 큐 분리), Redis 7, Flower |
| DB | MariaDB 11.4 |
| AI | Ollama (gemma3:latest 추출, exaone3.5:2.4b 채팅), ChromaDB 0.5 |
| OCR | PaddleOCR (커스텀 파인튜닝), Tesseract, EasyOCR, Pororo |
| 문서 | PyPDF2, pdf2image, pypdfium2, pyhwp + LibreOffice |
| Infra | Docker Compose, NVIDIA GPU 지원 |

## 5. 실행 방법

### 5-1. Docker 실행 (권장)

Ollama를 Docker로 함께 실행할 경우 `--profile ollama` 옵션을 추가합니다.

```bash
cd pdf-summary

# Ollama 없이 (로컬 Ollama 사용)
docker compose up --build

# Ollama 컨테이너 포함
docker compose --profile ollama up --build
```

기본 포트:

| 서비스 | 호스트 포트 |
| --- | --- |
| frontend | 5173 |
| backend (FastAPI) | 8000 |
| websocket (Socket.IO) | 8001 |
| MariaDB | 3307 |
| Redis | 6379 |
| ChromaDB | 8002 |
| Ollama (profile) | 11434 |
| Flower | 5555 |

종료/초기화:

```bash
docker compose down
docker compose down -v   # 볼륨(DB·Chroma·Ollama) 포함 삭제
```

### 5-2. 로컬 실행

```bash
conda env create -f environment.yml
conda activate tfod

cd pdf-summary/backend
pip install -r requirements.txt
mysql -u root -p < database_migration.sql
python main.py

cd ../frontend
npm install
npm run dev
```

접속:

- API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- Frontend: http://localhost:5173

## 6. 백엔드 통합 요약

### 라우터 구성

| 접두사 | 역할 |
| --- | --- |
| /auth | 로그인·회원가입·소셜 로그인·세션·계정 찾기 |
| /api/documents | 추출·요약·번역·문서 CRUD·다운로드 |
| /api/admin | 사용자·문서·시스템·결제 로그 |
| /api/payments | KakaoPay ready/approve |
| /socket.io | Socket.IO 웹소켓 앱 마운트 |

### 핵심 테이블

- users
- user_sessions
- pdf_documents
- admin_activity_logs
- payment_transactions

### Celery 워커 구성

- **worker_ocr**: OCR 큐(`-Q ocr`), concurrency=1, GPU 지원
- **worker_llm**: LLM 큐(`-Q llm`), concurrency=2

### 대표 엔드포인트

```
POST /auth/login
POST /auth/register
GET  /auth/sessions/validate
POST /api/documents/extract
POST /api/documents/summarize-document
POST /api/documents/translate
GET  /api/admin/documents
GET  /api/admin/documents/payment-logs
POST /api/payments/kakao/ready
POST /api/payments/kakao/approve
```

## 7. 프론트엔드 통합 요약

### 주요 페이지

| 페이지 | 경로 | 설명 |
| --- | --- | --- |
| HomeHub | / | 홈 허브 |
| PdfSummary | /pdf-summary | 문서 업로드·OCR·요약·번역 |
| ChatSummary | /chat-summary | 문서 기반 대화형 Q&A |
| MyPage | /mypage | 이력 조회·프로필 관리 |
| UserList | /userlist | 전체 요약 목록·결제 |
| AdminDashboard | /admin | 통합 관리자 대시보드 |
| KakaoSuccess | /payments/kakao/success | 결제 성공 콜백 |
| KakaoFail | /payments/kakao/fail | 결제 실패 콜백 |

### 라우팅

- 공개: `/login`, `/register`, `/payments/kakao/success`, `/payments/kakao/fail`
- 보호: `/`, `/pdf-summary`, `/chat-summary`, `/mypage`, `/userlist`, `/admin`

### 결제 동작 흐름

1. UserList에서 결제 대상 문서 선택
2. `POST /api/payments/kakao/ready` 호출
3. KakaoPay 결제창 팝업 오픈
4. 팝업 콜백 페이지(`/payments/kakao/success|fail`)에서 승인/실패 처리
5. `postMessage`로 부모창(UserList) 상태 즉시 갱신

## 8. 환경 변수

백엔드 파일: `pdf-summary/backend/.env`

### DB / 공통

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pdf_summary
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### AI / 큐

```env
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
EXTRACT_DEFAULT_MODEL=gemma3:latest
CHAT_DEFAULT_MODEL=exaone3.5:2.4b
CHAT_NUM_CTX=4096
CHAT_NUM_PREDICT=900
CHAT_REPEAT_PENALTY=1.1
CHROMA_BASE_URL=http://localhost:8000
CHROMA_COLLECTION=documents
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### OCR

```env
OCR_USE_GPU=true
PADDLE_DEVICE=gpu:0
PADDLE_CUSTOM_MODEL_DIR=/app/paddletrain
TESSDATA_PREFIX=/tessdata
LIBREOFFICE_PATH=/usr/bin/soffice
```

### KakaoPay (결제 전용)

```env
KAKAO_PAY_SECRET_KEY=YOUR_SECRET_KEY
KAKAO_PAY_CID=TC0ONETIME
FRONTEND_BASE_URL=http://localhost:5173
```

### 알림

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

> 결제 키(`KAKAO_PAY_*`)와 소셜 로그인 키(`KAKAO_CLIENT_ID`)는 별도입니다.

## 9. 결제 정책

- 공개+중요 문서만 결제 대상
- 문서 소유자/관리자는 결제 면제
- 결제 이력은 `payment_transactions` 테이블에 저장
- 관리자 결제 로그 조회: `GET /api/admin/documents/payment-logs`

## 10. 상세 문서

- Backend 상세: [pdf-summary/backend/README.md](pdf-summary/backend/README.md)
- Frontend 상세: [pdf-summary/frontend/README.md](pdf-summary/frontend/README.md)
