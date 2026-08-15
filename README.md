# WebClean API

Turn a messy webpage into clean, structured data.

Give it a URL, get back a JSON object with the page title, description,
email addresses, phone numbers, business hours, links, and word count.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive test page,
or call it directly with your API key:

```bash
curl -H "X-API-Key: demo-free" "http://127.0.0.1:8000/api/extract?url=https://example.com"
```

Check your plan and remaining quota:

```bash
curl -H "X-API-Key: demo-free" "http://127.0.0.1:8000/api/quota"
```

## API keys

Requests need an `X-API-Key` header. Two demo keys are built in:

| Key        | Tier  | Per minute | Per month |
| ---------- | ----- | ---------- | --------- |
| `demo-free` | free | 10         | 50        |
| `demo-pro`  | pro  | 60         | 5000      |

Set your own keys on Render with an `API_KEYS` environment variable
(a JSON object — this overrides the demo keys):

```json
{
  "your-secret-key": {"tier": "free", "per_minute": 10, "per_month": 50},
  "another-key":     {"tier": "pro",  "per_minute": 60, "per_month": 5000}
}
```

Rate limits are tracked in memory per process. For a single Render free
instance this is fine; scale to Redis if you run multiple instances.

## Example response

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "meta_description": "",
  "emails": ["info@example.com"],
  "phones": ["(555) 123-4567"],
  "hours": ["9:00 AM - 5:00 PM"],
  "links": ["https://example.com/about"],
  "word_count": 12
}
```

## Run tests

```bash
pytest
```
