import os
from typing import AsyncIterator

from services.ai_service import (
    summarize_text as _summarize_text,
    summarize_text_stream as _summarize_text_stream,
    translate_to_english as _translate_to_english,
    get_available_models as _get_available_models,
    categorize_document as _categorize_document,
)


EXTRACT_DEFAULT_MODEL = os.getenv("EXTRACT_DEFAULT_MODEL", "gemma3:latest")


async def summarize_text(text: str, model: str = EXTRACT_DEFAULT_MODEL) -> str:
    selected_model = model or EXTRACT_DEFAULT_MODEL
    return await _summarize_text(text=text, model=selected_model)


async def summarize_text_stream(
    text: str,
    model: str = EXTRACT_DEFAULT_MODEL,
) -> AsyncIterator[str]:
    selected_model = model or EXTRACT_DEFAULT_MODEL
    async for token in _summarize_text_stream(text=text, model=selected_model):
        yield token


async def translate_to_english(text: str, model: str = EXTRACT_DEFAULT_MODEL) -> str:
    selected_model = model or EXTRACT_DEFAULT_MODEL
    return await _translate_to_english(text=text, model=selected_model)


async def get_available_models() -> list:
    return await _get_available_models()


async def categorize_document(title: str = "", model: str = EXTRACT_DEFAULT_MODEL) -> str:
    selected_model = model or EXTRACT_DEFAULT_MODEL
    return await _categorize_document(title=title, model=selected_model)
