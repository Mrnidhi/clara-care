"""
Reports Module
PDF report generation for cognitive health summaries
"""

from .foxit_client import FoxitClient
from .generator import ReportGenerator

__all__ = ["FoxitClient", "ReportGenerator"]
