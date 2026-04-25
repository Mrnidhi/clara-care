# You.com Integration Guide

## Overview
ClaraCare uses the You.com Search API to provide real-time information and era-specific "nostalgia" content. This grounded approach ensures Clara can answer current questions and engage in meaningful reminiscence without hallucinations.

**Key Features**:
- **Nostalgia Mode**: Triggers era-specific content (music, news, events) from the patient's "golden years" (ages 15-25).
- **Real-time Q&A**: Answers questions about weather, news, and facts with live web data.
- **Citations**: All responses are backed by source URLs.

## Setup

1.  **Get API Key**: Visit [you.com/platform](https://you.com/platform) to get your API key.
2.  **Add to `.env`**:
    ```bash
    YOUCOM_API_KEY=your_api_key_here
    ```

## Usage

### 1. Nostalgia Search (`backend/app/nostalgia/youcom_client.py`)
Searches for content from a specific era.
```python
client = YouComClient()
# Patient born 1951 -> Golden years 1966-1976
result = await client.search_nostalgia(birth_year=1951, trigger_reason="feeling lonely")
# Returns: { "music": ["The Beatles..."], "events": ["Moon landing..."], "era": "1966-1976" }
```

### 2. Real-time Search
Standard web search for current information.
```python
result = await client.search_realtime("weather in San Francisco")
# Returns: { "answer": "Sunny, 68°F...", "citations": ["weather.com..."] }
```

## Testing

Run the test script to verify your API key and connection:
```bash
cd backend
python3 -c "
from app.nostalgia.youcom_client import YouComClient
import asyncio, os
async def test():
    client = YouComClient(api_key=os.getenv('YOUCOM_API_KEY'))
    # Nostalgia
    print('🎵 Nostalgia:', (await client.search_nostalgia(1951))['music'][:2])
    # Realtime
    print('🌤️  Weather:', (await client.search_realtime('weather today'))['answer'][:50])
    await client.close()
asyncio.run(test())
"
```

## Troubleshooting
- **No API Key**: The client will fallback to a built-in library of generic era-appropriate content (1950s-1990s).
- **Rate Limits**: Check your usage on the You.com platform dashboard.
