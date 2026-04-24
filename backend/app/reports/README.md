# Cognitive Report PDF Generation

## Is Foxit integrated?

**Yes - fully integrated with dynamic template generation.**

- When **`FOXIT_DOCUMENT_GENERATION_CLIENT_ID`** and **`FOXIT_DOCUMENT_GENERATION_API_SECRET`** are set, the backend calls the [Foxit Document Generation API](https://developers.foxit.com/document-generation-api) to produce PDFs from a dynamically generated DOCX template.
- When those env vars are **not** set, the backend uses a **mock PDF** with the same visual styling (tables, colors, formatting).

## Template Generation (NEW!)

**Templates are generated dynamically using python-docx** - no template files needed!

The `_get_default_template_base64()` method in `foxit_client.py`:
1. Creates a Document() object programmatically
2. Adds professional styling:
   - Centered blue title (24pt)
   - Styled tables for patient info and scores
   - Color-coded status indicators
   - Formatted sections with proper spacing
3. Inserts merge tags: `{{ patient_name }}`, `{{ cognitive_score }}`, etc.
4. Converts to Base64 and sends to Foxit API

**Benefits:**
- ✅ No binary DOCX files to version control
- ✅ Consistent styling across all reports
- ✅ Easy to modify (just edit Python code)
- ✅ Template evolves with code changes

## How the PDF is generated (flow)

```
HTTP GET /api/reports/{patient_id}/cognitive-report?days=30
         │
         ▼
  routes/reports.py  →  download_cognitive_report(patient_id, days)
         │
         ▼
  reports/generator.py  →  ReportGenerator.generate_cognitive_report(patient_id, days)
         │
         │  1. data_store.get_patient(patient_id)
         │  2. data_store.get_cognitive_trends(patient_id, days)
         │  3. data_store.get_cognitive_baseline(patient_id)
         │  4. data_store.get_alerts(patient_id)
         │  5. data_store.get_conversations(patient_id)
         │  6. _calculate_overall_score(trends, baseline)
         │  7. _calculate_trend_direction(trends)
         │  8. _generate_recommendations(trends, alerts, baseline)
         │  9. Build template_data (patient_name, cognitive_score, recommendations, etc.)
         │
         ▼
  reports/foxit_client.py  →  FoxitClient.generate_cognitive_report_pdf(patient_data=template_data)
         │
         ├── If Foxit credentials are set:
         │      • Generate DOCX template dynamically using python-docx
         │      • Convert template to Base64
         │      • POST to Foxit: /document-generation/api/GenerateDocumentBase64
         │      • Payload: outputFormat=pdf, documentValues={...}, base64FileString=<generated template>
         │      • Returns: Professional PDF with filled data
         │
         └── If Foxit credentials are NOT set:
                • _generate_mock_pdf(patient_data)  →  Creates a similar-styled PDF directly
                • Same visual appearance, just generated client-side instead of via Foxit
```

## Files

| File | Role |
|------|------|
| **`backend/app/routes/reports.py`** | HTTP endpoint: `GET /api/reports/{patient_id}/cognitive-report?days=7..90`. Calls generator, returns PDF response. |
| **`backend/app/reports/generator.py`** | Fetches patient, trends, baseline, alerts, conversations; computes score, trend, recommendations; builds `template_data`; calls Foxit client. |
| **`backend/app/reports/foxit_client.py`** | If credentials set: call Foxit API with DOCX template. If not: `_generate_mock_pdf()` builds the placeholder PDF you see. |

## Enabling full Foxit-generated reports

1. Set in backend `.env` (see `backend/.env.example`):
   - `FOXIT_DOCUMENT_GENERATION_CLIENT_ID`
   - `FOXIT_DOCUMENT_GENERATION_API_SECRET`
   - Optionally `FOXIT_BASE_URL` (default: `https://na1.fusion.foxit.com`)

2. Provide a DOCX template with text tags (e.g. `{{patient_name}}`, `{{cognitive_score}}`, `{{report_date}}`, `{{recommendations}}`) and pass its Base64 string to the client (or implement loading in `_get_default_template_base64()` in `foxit_client.py`).

Until then, the PDF you get is the **backend-built placeholder** from `_generate_mock_pdf()`.
