"""
Celery application configuration for background tasks.
"""
from celery import Celery
import logging

from config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "unified_assistant",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks.export_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'tasks.export_tasks.generate_export': {'queue': 'exports'},
    },
    task_default_queue='default',
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression='gzip',
    result_compression='gzip',
    result_expires=3600,  # 1 hour
)

# Task retry settings
celery_app.conf.task_default_retry_delay = 60
celery_app.conf.task_max_retries = 3

logger.info("Celery app configured successfully")
