"""
Cognitive Health Report Generator
Creates downloadable PDF reports for families
"""

import logging
from datetime import datetime, UTC, date

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates cognitive health reports as PDFs
    Combines data from Sanity with Foxit PDF generation
    """
    
    def __init__(self, data_store, foxit_client):
        """
        Args:
            data_store: DataStore instance (SanityDataStore or InMemoryDataStore)
            foxit_client: FoxitClient instance
        """
        self.data_store = data_store
        self.foxit_client = foxit_client
    
    async def generate_cognitive_report(
        self,
        patient_id: str,
        days: int = 30
    ) -> bytes:
        """
        Generate comprehensive cognitive health report PDF
        
        Args:
            patient_id: Patient identifier
            days: Number of days to include in report (default 30)
        
        Returns:
            PDF bytes ready for download
        """
        logger.info(f"Generating cognitive report for {patient_id} ({days} days)")
        
        # 1. Fetch patient data
        patient = await self.data_store.get_patient(patient_id)
        if not patient:
            logger.error(f"Patient not found: {patient_id}")
            return self._error_pdf("Patient not found")
        
        # 2. Fetch cognitive trends
        trends = await self.data_store.get_cognitive_trends(patient_id, days)
        
        # 3. Fetch baseline
        baseline = await self.data_store.get_cognitive_baseline(patient_id)
        
        # 4. Fetch recent alerts
        alerts = await self.data_store.get_alerts(patient_id, limit=10)
        
        # 5. Fetch recent conversations
        conversations = await self.data_store.get_conversations(patient_id, limit=10)
        
        # 6. Calculate summary statistics
        cognitive_score = self._calculate_overall_score(trends, baseline)
        trend_direction = self._calculate_trend_direction(trends)
        
        # 7. Assemble template data
        template_data = {
            "patient_name": patient.get("name", "Unknown"),
            "patient_age": patient.get("age", "Unknown"),
            "report_date": date.today().isoformat(),
            "report_period_days": days,
            "cognitive_score": cognitive_score,
            "trend": trend_direction,
            
            # Baseline metrics
            "baseline_vocabulary": baseline.get("vocabulary_diversity", 0) if baseline else 0,
            "baseline_coherence": baseline.get("topic_coherence", 0) if baseline else 0,
            "baseline_established": baseline.get("established", False) if baseline else False,
            
            # Current averages
            "avg_vocabulary": self._average_metric(trends, "vocabulary_diversity"),
            "avg_coherence": self._average_metric(trends, "topic_coherence"),
            "avg_repetition": self._average_metric(trends, "repetition_rate"),
            
            # Alert summary
            "total_alerts": len(alerts),
            "high_severity_alerts": len([a for a in alerts if a.get("severity") == "high"]),
            
            # Conversation summary
            "total_conversations": len(conversations),
            
            # Recommendations
            "recommendations": self._generate_recommendations(trends, alerts, baseline)
        }
        
        # 8. Generate PDF via Foxit Document Generation API
        pdf_bytes = await self.foxit_client.generate_cognitive_report_pdf(
            patient_data=template_data
        )
        
        logger.info(f"Report generated successfully ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    
    def _calculate_overall_score(self, trends: list, baseline: dict) -> int:
        """
        Calculate overall cognitive score (0-100)
        Based on current performance vs baseline
        """
        if not trends or not baseline or not baseline.get("established"):
            return 0
        
        # Get recent average (last 7 conversations)
        recent = trends[-7:] if len(trends) >= 7 else trends
        
        vocab_avg = self._average_metric(recent, "vocabulary_diversity")
        coherence_avg = self._average_metric(recent, "topic_coherence")
        repetition_avg = self._average_metric(recent, "repetition_rate")
        
        vocab_baseline = baseline.get("vocabulary_diversity", 0.5)
        coherence_baseline = baseline.get("topic_coherence", 0.8)
        repetition_baseline = baseline.get("repetition_rate", 0.05)
        
        # Score components (0-100)
        vocab_score = min(100, (vocab_avg / vocab_baseline * 100)) if vocab_baseline > 0 else 50
        coherence_score = min(100, (coherence_avg / coherence_baseline * 100)) if coherence_baseline > 0 else 50
        repetition_score = max(0, 100 - (repetition_avg / repetition_baseline * 100)) if repetition_baseline > 0 else 50
        
        # Weighted average
        overall = (vocab_score * 0.4 + coherence_score * 0.4 + repetition_score * 0.2)
        
        return int(overall)
    
    def _calculate_trend_direction(self, trends: list) -> str:
        """
        Determine if cognitive metrics are improving, stable, or declining
        """
        if len(trends) < 4:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid = len(trends) // 2
        first_half = trends[:mid]
        second_half = trends[mid:]
        
        vocab_first = self._average_metric(first_half, "vocabulary_diversity")
        vocab_second = self._average_metric(second_half, "vocabulary_diversity")
        
        coherence_first = self._average_metric(first_half, "topic_coherence")
        coherence_second = self._average_metric(second_half, "topic_coherence")
        
        vocab_change = (vocab_second - vocab_first) / vocab_first if vocab_first > 0 else 0
        coherence_change = (coherence_second - coherence_first) / coherence_first if coherence_first > 0 else 0
        
        avg_change = (vocab_change + coherence_change) / 2
        
        if avg_change > 0.05:
            return "improving"
        elif avg_change < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _average_metric(self, trends: list, metric_name: str) -> float:
        """Calculate average of a metric across trends"""
        values = [t.get(metric_name) for t in trends if t.get(metric_name) is not None]
        return sum(values) / len(values) if values else 0.0
    
    def _generate_recommendations(
        self,
        trends: list,
        alerts: list,
        baseline: dict
    ) -> str:
        """Generate recommendations based on data"""
        recommendations = []
        
        # Check for high-severity alerts
        high_alerts = [a for a in alerts if a.get("severity") == "high"]
        if high_alerts:
            recommendations.append("• Consult with healthcare provider about recent high-priority alerts")
        
        # Check for declining trends
        if len(trends) >= 4:
            trend = self._calculate_trend_direction(trends)
            if trend == "declining":
                recommendations.append("• Consider scheduling cognitive assessment with doctor")
                recommendations.append("• Increase engagement activities and social interaction")
        
        # Check repetition rate
        recent_repetition = self._average_metric(trends[-7:], "repetition_rate")
        if recent_repetition > 0.15:
            recommendations.append("• Monitor for repetitive storytelling patterns")
        
        # Default positive recommendation
        if not recommendations:
            recommendations.append("• Continue regular daily conversations")
            recommendations.append("• Maintain current care routine")
        
        return "\n".join(recommendations)
    
    def _error_pdf(self, error_message: str) -> bytes:
        """Generate error PDF"""
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
50 700 Td
(Error: {error_message}) Tj
ET
endstream
endobj
xref
0 5
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF
"""
        return pdf_content.encode('latin-1')
