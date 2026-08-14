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
or call it directly:

```bash
curl "http://127.0.0.1:8000/api/extract?url=https://example.com"
```

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
