from fastapi import FastAPI, HTTPException, Query

from scraper import scrape_url

app = FastAPI(
    title="WebClean API",
    description="Turn a messy webpage into clean, structured data.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "WebClean API",
        "usage": "GET /api/extract?url=https://example.com",
        "interactive_docs": "/docs",
    }


@app.get("/api/extract")
def extract(url: str = Query(..., description="The messy webpage URL to clean up")):
    try:
        return scrape_url(url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
