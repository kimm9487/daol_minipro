import httpx
from fastapi import HTTPException

# Ollama 기본 설정
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma3:latest"  


async def summarize_text(text: str, model: str = DEFAULT_MODEL) -> str:
    """
    Ollama API를 호출하여 텍스트를 요약합니다.
    """
    MAX_CHARS = 8000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n[... 이하 내용 생략 ...]"

    prompt = f"""다음 PDF 문서 내용을 한국어로 명확하고 간결하게 요약해줘.

요약 형식:
1. 전체 내용을 3~5문장으로 핵심 요약
2. 주요 키워드 5개 이하
3. 중요 포인트 3~5가지 (bullet point)

--- 문서 내용 ---
{text}
---

위 내용을 위 형식에 맞게 요약해줘."""

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Ollama API 오류: {response.status_code} - 모델({model})이 설치되어 있는지 확인하세요."
                )

            data = response.json()
            return data.get("response", "요약 결과를 가져올 수 없습니다.")

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령어로 서버를 실행해주세요."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 요약 중 오류 발생: {str(e)}")


async def translate_to_english(text: str, model: str = DEFAULT_MODEL) -> str:
    """
    한국어 텍스트를 영어로 번역합니다.
    """
    MAX_CHARS = 6000
    if len(text) > MAX_CHARS:
        # 긴 텍스트는 청킹해서 번역
        return await _translate_long_text(text, model)
    
    prompt = f"""다음 한국어 텍스트를 자연스러운 영어로 번역해주세요. 
전문용어는 적절히 유지하고, 문맥과 의미를 정확히 전달해주세요.

한국어 텍스트:
{text}

영어 번역:"""

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"번역 API 오류: {response.status_code} - 모델({model})이 설치되어 있는지 확인하세요."
                )

            data = response.json()
            return data.get("response", "번역 결과를 가져올 수 없습니다.")

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령어로 서버를 실행해주세요."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"번역 중 오류 발생: {str(e)}")


async def _translate_long_text(text: str, model: str) -> str:
    """
    긴 텍스트를 청킹해서 번역하고 결합합니다.
    """
    CHUNK_SIZE = 4000
    OVERLAP = 200
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        
        # 문장 경계에서 자르기 시도
        if end < len(text):
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            boundary = max(last_period, last_newline)
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary + 1
        
        chunk = text[start:end]
        chunks.append(chunk)
        
        start = max(0, end - OVERLAP)
        if start >= end:
            break
    
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        try:
            translated = await translate_to_english(chunk, model)
            translated_chunks.append(translated)
        except Exception as e:
            translated_chunks.append(f"[번역 실패 구간 {i+1}: {str(e)}]")
    
    return "\n\n".join(translated_chunks)


async def get_available_models() -> list:
    """
    Ollama에 설치된 모델 목록을 반환합니다.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
    except Exception:
        return []
