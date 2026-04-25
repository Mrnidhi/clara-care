# Sanity CMS Integration Guide

## Overview
Sanity CMS serves as the backend database for ClaraCare, storing patient profiles, conversation logs, family member details, and wellness digests. It enables a structured content approach to longitudinal health tracking.

**Key Features**:
- **Structured Content**: 5 core document types (`patient`, `conversation`, `familyMember`, `wellnessDigest`, `alert`)
- **Real-time Queries**: GROQ queries via `SanityDataStore`
- **MCP Server**: Integrated for AI-assisted development

## Architecture
The FastAPI backend interacts with Sanity via the `SanityDataStore` class (`backend/app/storage/sanity.py`), which implements the `DataStore` protocol. It handles:
- Retrieving patient context for the voice agent
- Logging conversations and cognitive metrics
- Storing alerts and family notifications

## Environment Setup

Add these keys to `backend/.env`:
```bash
SANITY_PROJECT_ID=your_sanity_project_id
SANITY_DATASET=production
SANITY_TOKEN=your_sanity_token
# Get token: https://www.sanity.io/manage/personal/tokens (Editor permissions required)
```

## Data Models

### 1. Patient
Core profile containing demographics and preferences.
```javascript
{
  _type: 'patient',
  name: 'Dorothy Chen',
  birth_year: 1951,
  medications: [...],
  preferences: { communication_style: 'warm' }
}
```

### 2. Conversation
Stores transcripts and analysis from voice sessions.
```javascript
{
  _type: 'conversation',
  patient: { _ref: 'patient-id' },
  transcript: '...',
  detected_mood: 'happy',
  cognitive_metrics: { vocabulary_diversity: 0.72 }
}
```

### 3. Family Member
Contact info for alerts.
```javascript
{
  _type: 'familyMember',
  patient: { _ref: 'patient-id' },
  email: 'sarah@example.com',
  notification_preferences: ['email', 'sms']
}
```

### 4. Wellness Digest & 5. Alert
Weekly summaries and urgent notifications.

## Testing Integration

Run the connection test script:
```bash
cd backend
python3 -c "
from app.storage.sanity import SanityDataStore
import asyncio, os
async def test():
    store = SanityDataStore(
        project_id=os.getenv('SANITY_PROJECT_ID'),
        dataset=os.getenv('SANITY_DATASET'),
        token=os.getenv('SANITY_TOKEN')
    )
    patients = await store.get_all_patients()
    print(f'✅ Found {len(patients)} patients')
    await store.close()
asyncio.run(test())
"
```

## Seed Data
Populate the CMS with test data using the seed script:
```bash
cd backend
python3 scripts/seed_sanity.py
```
This creates a sample patient (Dorothy), family member (Sarah), and historical conversations.
