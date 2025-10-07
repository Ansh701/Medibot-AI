import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-medibot-2024'

    # Security Configuration
    SESSION_COOKIE_SECURE = not os.environ.get('FLASK_ENV') == 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Rate Limiting
    RATELIMIT_STORAGE_URL = "redis://localhost:6379/1" if os.environ.get('REDIS_URL') else "memory://"

    # Medical AI Configuration
    MAX_QUERY_LENGTH = 1000
    MAX_CONTEXT_LENGTH = 4000
    MEDICAL_CONFIDENCE_THRESHOLD = 0.7

    # Vector Search Configuration
    VECTOR_SEARCH_K = 8
    HYBRID_SEARCH_WEIGHT = 0.7
    RERANK_TOP_K = 5

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    AUDIT_LOG_RETENTION_DAYS = 90

    # HIPAA Compliance
    ENCRYPT_CONVERSATIONS = True
    AUTO_DELETE_CONVERSATIONS = True
    CONVERSATION_RETENTION_HOURS = 24
