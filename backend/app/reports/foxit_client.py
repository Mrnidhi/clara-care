"""
Foxit API Client
Handles PDF document generation using Foxit Document Generation API
Based on: https://developers.foxit.com/
"""

import logging
import os
import base64
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class FoxitClient:
    """
    Client for Foxit Document Generation API
    Generates cognitive health reports as PDF documents
    
    API Documentation: https://developers.foxit.com/document-generation-api
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Foxit Document Generation client
        
        Args:
            client_id: Foxit client ID (or from FOXIT_DOCUMENT_GENERATION_CLIENT_ID env var)
            client_secret: Foxit client secret (or from FOXIT_DOCUMENT_GENERATION_API_SECRET env var)
            base_url: Foxit API base URL (or from FOXIT_BASE_URL env var)
        """
        self.client_id = client_id or os.getenv("FOXIT_DOCUMENT_GENERATION_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("FOXIT_DOCUMENT_GENERATION_API_SECRET")
        self.base_url = base_url or os.getenv("FOXIT_BASE_URL", "https://na1.fusion.foxit.com")
        
        if self.client_id and self.client_secret:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            logger.info("✓ FoxitClient initialized with Document Generation API credentials")
        else:
            self._client = None
            logger.warning("⚠ FoxitClient initialized without credentials - will use mock PDFs")
    
    async def generate_cognitive_report_pdf(
        self,
        patient_data: Dict[str, Any],
        template_base64: Optional[str] = None
    ) -> bytes:
        """
        Generate cognitive health report PDF from template
        
        Uses Foxit Document Generation API to populate template with patient data.
        Template should contain text tags like {{patient_name}}, {{cognitive_score}}, etc.
        
        Args:
            patient_data: Dict containing:
                - patient_name: Patient's full name
                - report_date: Date of report
                - cognitive_score: Overall cognitive score (0-100)
                - memory_score: Memory subscore
                - language_score: Language subscore
                - attention_score: Attention subscore
                - trends: Recent trend analysis
                - recommendations: List of recommendations
                - alert_summary: Summary of alerts
            template_base64: Optional Base64-encoded DOCX template
                            If not provided, uses built-in simple template
        
        Returns:
            PDF bytes
        """
        if not self._client:
            logger.info("Foxit API not configured - using mock PDF")
            return self._generate_mock_pdf(patient_data)
        
        try:
            # Use provided template or generate simple default
            if not template_base64:
                template_base64 = self._get_default_template_base64()
            
            # Prepare document values matching template text tags
            document_values = {
                "patient_name": patient_data.get("patient_name", "Unknown"),
                "report_date": patient_data.get("report_date", ""),
                "cognitive_score": str(patient_data.get("cognitive_score", 0)),
                "memory_score": str(patient_data.get("memory_score", 0)),
                "language_score": str(patient_data.get("language_score", 0)),
                "attention_score": str(patient_data.get("attention_score", 0)),
                "trends": patient_data.get("trends", "No trends available"),
                "recommendations": patient_data.get("recommendations", ""),
                "alert_summary": patient_data.get("alert_summary", "No alerts"),
            }
            
            # Foxit Document Generation API request
            payload = {
                "outputFormat": "pdf",
                "currencyCulture": "en-US",
                "documentValues": document_values,
                "base64FileString": template_base64
            }
            
            logger.info(f"Generating PDF for patient: {document_values['patient_name']}")
            
            response = await self._client.post(
                "/document-generation/api/GenerateDocumentBase64",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                # Foxit returns Base64-encoded PDF in response
                pdf_base64 = result.get("base64FileString", "")
                if pdf_base64:
                    pdf_bytes = base64.b64decode(pdf_base64)
                    logger.info(f"✓ Generated PDF: {len(pdf_bytes)} bytes")
                    return pdf_bytes
                else:
                    logger.error("Foxit API returned empty PDF")
                    return self._generate_mock_pdf(patient_data)
            else:
                logger.warning(f"Foxit API error {response.status_code}: {response.text}")
                return self._generate_mock_pdf(patient_data)
                
        except httpx.HTTPError as e:
            logger.warning(f"Foxit API request failed: {e}")
            return self._generate_mock_pdf(patient_data)
        except Exception as e:
            logger.error(f"Unexpected error in Foxit document generation: {e}")
            return self._generate_mock_pdf(patient_data)
    
    def _get_default_template_base64(self) -> str:
        """
        Returns Base64-encoded minimal DOCX template
        Template contains text tags for patient data
        
        In production, load from file or S3.
        For now, returns placeholder.
        """
        # TODO: Create actual DOCX template with text tags and convert to Base64
        # Template should include:
        # {{patient_name}}, {{report_date}}, {{cognitive_score}}
        # {{memory_score}}, {{language_score}}, {{attention_score}}
        # {{trends}}, {{recommendations}}, {{alert_summary}}
        
        logger.warning("Using placeholder template - should load real DOCX template")
        
        # Placeholder - in production, return actual template Base64
        return ""
    
    def _generate_mock_pdf(self, patient_data: Dict[str, Any]) -> bytes:
        """
        Generate a mock PDF for development/fallback
        Returns a minimal valid PDF document with patient data
        """
        patient_name = patient_data.get("patient_name", "Patient")
        report_date = patient_data.get("report_date", "Unknown")
        cognitive_score = patient_data.get("cognitive_score", 0)
        memory_score = patient_data.get("memory_score", 0)
        language_score = patient_data.get("language_score", 0)
        attention_score = patient_data.get("attention_score", 0)
        
        logger.info(f"Generating mock PDF for {patient_name}")
        
        # Minimal PDF structure with patient data
        pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica-Bold
>>
/F2 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 800
>>
stream
BT
/F1 20 Tf
50 720 Td
(ClaraCare Cognitive Health Report) Tj
0 -30 Td
/F2 12 Tf
(Generated by ClaraCare AI System) Tj
0 -40 Td
/F1 14 Tf
(Patient Information) Tj
0 -25 Td
/F2 11 Tf
(Name: {patient_name}) Tj
0 -18 Td
(Report Date: {report_date}) Tj
0 -35 Td
/F1 14 Tf
(Cognitive Assessment Scores) Tj
0 -25 Td
/F2 11 Tf
(Overall Cognitive Score: {cognitive_score}/100) Tj
0 -18 Td
(Memory: {memory_score}/100) Tj
0 -18 Td
(Language: {language_score}/100) Tj
0 -18 Td
(Attention: {attention_score}/100) Tj
0 -35 Td
/F1 14 Tf
(Summary) Tj
0 -25 Td
/F2 11 Tf
(This is a development placeholder report.) Tj
0 -18 Td
(Full report generation requires Foxit Document) Tj
0 -18 Td
(Generation API configuration with DOCX template.) Tj
0 -25 Td
(Contact: support@claracare.com) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000368 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
1220
%%EOF
"""
        return pdf_content.encode('latin-1')
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            logger.info("Closed FoxitClient HTTP client")
