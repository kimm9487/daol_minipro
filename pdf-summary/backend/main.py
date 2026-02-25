from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import summary
from database import init_db

app = FastAPI(title="PDF 문서 요약 시스템", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()  # 데이터베이스 초기화 (테이블 생성)

# 라우터 등록
app.include_router(summary.router, prefix="/api", tags=["summary"])


@app.get("/")
def root():
    return {"message": "PDF 요약 시스템 API 서버 실행 중"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
