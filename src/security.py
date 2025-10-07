import hashlib
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any
import html
import bleach
import os

logger = logging.getLogger(__name__)


class SecurityManager:
    """Enhanced security manager with HIPAA compliance features"""

    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (partial)
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
        ]

    def sanitize_input(self, user_input: str) -> str:
        """Comprehensive input sanitization"""
        if not user_input:
            return ""

        # HTML sanitization
        cleaned = html.escape(user_input)

        # Remove potentially sensitive information patterns
        for pattern in self.sensitive_patterns:
            cleaned = re.sub(pattern, '[REDACTED]', cleaned)

        # Additional cleaning with bleach
        cleaned = bleach.clean(cleaned, tags=[], attributes={}, strip=True)

        return cleaned.strip()

    def detect_medical_emergency(self, text: str) -> bool:
        """Detect potential medical emergency keywords"""
        emergency_keywords = [
            'suicide', 'kill myself', 'end my life', 'overdose',
            'chest pain', 'heart attack', 'stroke', 'bleeding heavily',
            'can\'t breathe', 'emergency', 'urgent', 'dying'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)

    def hash_session_id(self, session_id: str) -> str:
        """Create hashed version of session ID for logging"""
        return hashlib.sha256(session_id.encode()).hexdigest()[:16]


def audit_log(event_type: str, session_id: str, data: Dict[Any, Any]):
    """HIPAA-compliant audit logging"""
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "session_hash": SecurityManager().hash_session_id(session_id),
            "data": data
        }

        # Log to secure audit file
        with open('logs/audit.log', 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')

    except Exception as e:
        logger.error(f"Audit logging failed: {e}")


def medical_disclaimer_required(query_type: str) -> bool:
    """Determine if medical disclaimer is required"""
    high_risk_types = [
        'diagnosis', 'treatment', 'medication', 'emergency'
    ]
    return query_type in high_risk_types
