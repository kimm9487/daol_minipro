markdown# 📄 PDF 문서 요약 시스템

사용자가 PDF 파일을 업로드하면 텍스트를 추출하고, Ollama AI를 통해 요약한 결과를 화면에 표시하는 웹 애플리케이션입니다.

---

## 🖥️ 프로젝트 구조
```
pdf-summary/
├── backend/
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── database.py              # DB 연결 및 모델 정의
│   ├── .env                     # 환경변수 (DB 설정)
│   ├── requirements.txt         # 패키지 목록
│   ├── routers/
│   │   └── summary.py           # API 엔드포인트
│   └── services/
│       ├── pdf_service.py       # PDF 텍스트 추출
│       └── ai_service.py        # Ollama AI 요약
└── frontend/
    └── index.html               # 프론트엔드 UI
```

---

## ⚙️ 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI (Python) |
| AI | Ollama (gemma3:latest) |
| DB | MariaDB 11.4.0 |
| PDF 추출 | PyPDF2 |
| ORM | SQLAlchemy |

---

## 🚀 실행 방법

### 1. 가상환경 활성화
```bash
conda activate tfod
```

### 2. 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

### 3. 환경변수 설정

`backend/.env` 파일 생성:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=비밀번호
DB_NAME=pdf_summary
```

### 4. MariaDB 테이블 생성
```sql
CREATE DATABASE IF NOT EXISTS pdf_summary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pdf_summary;

CREATE TABLE pdf_documents (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    filename       VARCHAR(255) NOT NULL,
    extracted_text LONGTEXT,
    summary        LONGTEXT,
    model_used     VARCHAR(100),
    char_count     INT DEFAULT 0,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Ollama 실행
```bash
ollama serve
```

> 모델이 없을 경우: `ollama pull gemma3:latest`

### 6. 백엔드 서버 실행
```bash
cd backend
python main.py
```

> 서버 주소: http://localhost:8000  
> API 문서: http://localhost:8000/docs

### 7. 프론트엔드 실행

`frontend/index.html` 파일을 브라우저에서 열기

---

## 🔌 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/summarize` | PDF 업로드 → 텍스트 추출 → AI 요약 → DB 저장 |
| `GET` | `/api/models` | 설치된 Ollama 모델 목록 조회 |
| `POST` | `/api/download` | 요약 결과 TXT 다운로드 |

---

## 🗄️ DB 테이블 구조

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT | 자동 증가 PK |
| filename | VARCHAR(255) | 업로드 파일명 |
| extracted_text | LONGTEXT | PDF 원문 전체 |
| summary | LONGTEXT | AI 요약 결과 |
| model_used | VARCHAR(100) | 사용한 AI 모델명 |
| char_count | INT | 원문 글자 수 |
| created_at | DATETIME | 업로드 시간 |

---

## 📦 주요 패키지
```
fastapi
uvicorn
python-multipart
PyPDF2
httpx
python-dotenv
sqlalchemy
pymysql
```

---

## 📌 주의사항

- Ollama 서버가 실행 중이어야 AI 요약 기능이 작동합니다
- `frontend/index.html`을 브라우저에서 직접 열 경우 `main.py`의 CORS 설정에 `"null"`이 포함되어 있어야 합니다
- PDF가 이미지 기반인 경우 텍스트 추출이 되지 않을 수 있습니다
