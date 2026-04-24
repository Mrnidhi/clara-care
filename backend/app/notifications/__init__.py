"""
Notification Module
Email and SMS notification system for alerts and wellness digests
"""

from .email import EmailNotifier

__all__ = [
    "EmailNotifier"
]
