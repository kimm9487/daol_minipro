import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("pdf_summary", broker=broker_url, backend=result_backend)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=False,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=int(os.getenv("CELERY_TASK_TIME_LIMIT", "3600")),
    task_soft_time_limit=int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "3300")),
    result_expires=int(os.getenv("CELERY_RESULT_EXPIRES", "86400")),
    task_routes={
        "tasks.document_tasks.extract_document_task": {"queue": "ocr"},
        "tasks.document_tasks.summarize_document_task": {"queue": "llm"},
    },
    imports=("tasks.document_tasks",),
)
