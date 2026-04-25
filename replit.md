# ClaraCare - AI Elder Care Companion

## Overview
ClaraCare is an AI voice companion backend (FastAPI) that helps families care for aging parents. It provides daily check-in calls, cognitive health tracking, nostalgia mode, and smart alerts.

## Project Architecture
- **Backend**: Python FastAPI application in `backend/`
  - `backend/app/main.py` - Main FastAPI entry point
  - `backend/app/routes/` - API route handlers (patients, conversations, wellness, alerts, insights, reports)
  - `backend/app/cognitive/` - NLP-based cognitive analysis (analyzer, baseline tracker, alert engine, pipeline)
  - `backend/app/voice/` - Twilio voice integration (agent, bridge, outbound calls)
  - `backend/app/storage/` - Data storage (in-memory and Sanity CMS)
  - `backend/app/notifications/` - Email notifications via SMTP
  - `backend/app/reports/` - PDF report generation via Foxit
  - `backend/app/nostalgia/` - Nostalgia mode with You.com API
- **Sanity Studio**: `studio-claracare/` - CMS studio for managing patient data (separate tool, not the main app)
- **Docs**: `docs/` - Project documentation

## Running
- Backend runs on port 5000 via uvicorn with `--reload`
- Workflow: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload`

## Key Dependencies
- FastAPI, uvicorn, pydantic - Web framework
- spacy, sentence-transformers, scikit-learn - NLP/cognitive analysis
- httpx - HTTP client for external APIs
- aiosmtplib, jinja2 - Email notifications
- python-dotenv - Environment config

## External Services (optional, app runs without them)
- Sanity CMS (SANITY_PROJECT_ID, SANITY_DATASET, SANITY_TOKEN)
- Twilio (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)
- Deepgram (DEEPGRAM_API_KEY)
- You.com (YOUCOM_API_KEY)
- Foxit PDF Services (FOXIT_* variables)
- SMTP Email (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
