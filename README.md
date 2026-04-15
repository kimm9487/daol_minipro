# PDF Daol Project

PDF/HWP 문서 업로드부터 OCR, AI 요약/번역, 대화형 질의응답, 관리자 운영, 결제 연동까지 포함한 통합 플랫폼입니다.

## 1. 프로젝트 개요

- 문서 처리: PDF/HWP 업로드, 텍스트 추출, 요약, 번역
- 대화형 기능: 문서 기반 Q&A (RAG + Socket.IO)
- 사용자 기능: 마이페이지, 문서 이력 관리, 계정 관리
- 관리자 기능: 사용자/문서/시스템/결제 로그 통합 대시보드
- 결제 기능: KakaoPay 팝업 결제 및 상태 동기화

상세 문서:

- Backend: [pdf-summary/backend/README.md](pdf-summary/backend/README.md)
- Frontend: [pdf-summary/frontend/README.md](pdf-summary/frontend/README.md)

## 2. 최근 반영 사항 (2026-04)

### MyPage 프로필/탈퇴 UX 개선

- 프로필 수정에서 이메일 변경 UI를 차단했습니다.
    - 현재 이메일은 조회 전용으로 표시됩니다.
    - 저장 요청에서는 이메일 필드를 전송하지 않습니다.
- 회원 탈퇴 확인을 브라우저 alert/confirm에서 전용 모달로 변경했습니다.
    - 안내 문구: 탈퇴 책임 고지 + 복구 불가 고지
    - 확인 버튼 클릭 시에만 탈퇴 API를 호출합니다.

### 관리자 회원 삭제 안정성 강화

- 회원 삭제 시 결제 이력 정리 로직을 보강했습니다.
    - `payment_transactions.user_id == 대상 사용자`
    - 또는 `payment_transactions.document_id`가 대상 사용자의 문서인 경우
- 위 선삭제 후 문서(`pdf_documents`)를 삭제하여 FK 오류(1451) 재발 가능성을 낮췄습니다.

## 3. 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| Frontend | React 19, Vite 7, React Router DOM 7, react-hot-toast, socket.io-client |
| Backend | FastAPI 0.115, Uvicorn, SQLAlchemy 2, PyMySQL |
| Queue | Celery 5, Redis 7, Flower |
| DB | MariaDB 11.4 |
| AI/RAG | Ollama, ChromaDB |
| OCR | PaddleOCR(커스텀), Tesseract, EasyOCR, Pororo, PyPDF2 |
| Infra | Docker Compose, NVIDIA GPU |

## 4. 저장소 구조

```text
daol_minipro/
├── README.md
├── environment.yml
├── conda_packages.txt
├── conda_pip.txt
├── backend_logs.txt
├── package.json
└── pdf-summary/
        ├── docker-compose.yml
        ├── backend/
        │   ├── main.py
        │   ├── websocket_main.py
        │   ├── celery_app.py
        │   ├── database.py
        │   ├── routers/
        │   │   ├── auth/
        │   │   ├── admin/
        │   │   ├── document/
        │   │   ├── payment/
        │   │   └── websocket/
        │   ├── services/
        │   ├── tasks/
        │   ├── utils/
        │   └── README.md
        ├── frontend/
        │   ├── src/
        │   │   ├── components/
        │   │   ├── hooks/
        │   │   ├── pages/
        │   │   └── config/
        │   └── README.md
        ├── paddletrain/
        ├── tessdata/
        └── db-backups/
```

## 5. 실행 방법

### 5-1. Docker 실행 (권장)

```bash
cd pdf-summary

# 기본 실행 (Ollama는 외부/로컬 사용)
docker compose up --build

# Ollama 컨테이너 포함 실행
docker compose --profile ollama up --build
```

종료:

```bash
docker compose down
docker compose down -v
```

### 5-2. 로컬 실행

```bash
conda env create -f environment.yml
conda activate tfod

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

프론트:

```bash
cd pdf-summary/frontend
npm install
npm run dev
```

## 6. 서비스 포트

| 서비스 | 호스트 포트 | 비고 |
| --- | --- | --- |
| Frontend (Vite) | 5173 | 사용자 UI |
| Backend (FastAPI) | 8000 | REST API / docs |
| WebSocket | 8001 | Socket.IO |
| MariaDB | 3307 | 컨테이너 내부는 3306 |
| Redis | 6379 | Celery broker/backend |
| ChromaDB | 8002 | 컨테이너 내부는 8000 |
| Ollama (옵션) | 11434 | `--profile ollama` |
| Flower | 5555 | 큐 모니터링 |

## 7. 라우터/페이지 맵

### Backend 라우터

| Prefix | 설명 |
| --- | --- |
| /auth | 로그인/회원가입/세션/소셜/프로필/회원탈퇴 |
| /api/documents | 문서 CRUD, 추출/요약/번역, 다운로드 |
| /api/admin | 사용자/문서/시스템/결제 로그 관리 |
| /api/payments | KakaoPay ready/approve |
| /socket.io | Socket.IO 앱 마운트 |

### Frontend 주요 라우트

| Route | 접근 | 설명 |
| --- | --- | --- |
| /login | 공개 | 로그인 |
| /register | 공개 | 회원가입 |
| / | 보호 | HomeHub |
| /pdf-summary | 보호 | 업로드/OCR/요약/번역 |
| /chat-summary | 보호 | 문서 기반 Q&A |
| /mypage | 보호 | 이력/프로필/회원탈퇴 |
| /userlist | 보호 | 전체 목록/결제 |
| /admin | 보호 | 관리자 대시보드 |
| /payments/kakao/success | 공개 | 결제 성공 콜백 |
| /payments/kakao/fail | 공개 | 결제 실패 콜백 |

## 8. 환경 변수

백엔드 env 파일 위치: `pdf-summary/backend/.env`

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

참고:

- `KAKAO_PAY_*`는 결제용 키입니다.
- `KAKAO_CLIENT_ID`는 소셜 로그인용 키입니다.

## 9. 운영 정책

### 결제 정책

- 공개 + 중요 문서만 결제 대상
- 문서 소유자와 관리자는 결제 면제
- 결제 이력은 `payment_transactions`에 저장

### 계정/개인화 정책

- MyPage 프로필 수정: 이메일 변경 비활성화
- 회원 탈퇴: 확인 모달을 통한 명시적 동의 후 처리
- 탈퇴 시 문서/세션/로그/결제 이력 정리 후 계정 삭제

## 10. 트러블슈팅 체크리스트

### CORS + 500 에러가 같이 보일 때

- OPTIONS preflight 응답 상태를 먼저 확인합니다.
- 실제 원인은 백엔드 예외인 경우가 많으니 backend 로그를 같이 확인합니다.

### 회원 삭제 시 FK 오류(1451) 발생 시

- `payment_transactions` 선삭제 여부를 확인합니다.
- 특히 대상 사용자의 문서를 참조하는 결제 레코드까지 삭제 대상인지 확인합니다.

### PaddleOCR 관련 충돌/크래시

- `paddlepaddle`과 `paddlepaddle-gpu` 동시 설치 여부를 확인합니다.
- GPU 환경이 불안정하면 `OCR_USE_GPU=false`로 CPU 폴백을 적용합니다.

## 11. 빠른 링크

- Backend 상세 문서: [pdf-summary/backend/README.md](pdf-summary/backend/README.md)
- Frontend 상세 문서: [pdf-summary/frontend/README.md](pdf-summary/frontend/README.md)
