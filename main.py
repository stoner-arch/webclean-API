import json
import os
import time

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from scraper import scrape_url

app = FastAPI(
    title="WebClean API",
    description="Turn a messy webpage into clean, structured data.",
    version="0.2.0",
)

DEFAULT_KEYS = {
    "demo-free": ("free", 10, 50),
    "demo-pro": ("pro", 60, 5000),
    "wcf_bb9210f01cf9066e": ("free", 10, 50),
    "wcf_3ff8bf662940d799": ("pro", 60, 5000),
}

MONTH_SECONDS = 30 * 24 * 60 * 60


def load_keys() -> dict:
    raw = os.environ.get("API_KEYS")
    if not raw:
        return DEFAULT_KEYS
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return DEFAULT_KEYS
    result = {}
    for key, cfg in parsed.items():
        result[key] = (
            cfg.get("tier", "free"),
            int(cfg.get("per_minute", 10)),
            int(cfg.get("per_month", 50)),
        )
    return result


API_KEYS = load_keys()


class RateLimiter:
    def __init__(self) -> None:
        self.minute: dict[str, list[float]] = {}
        self.month: dict[str, list[float]] = {}

    def _prune(self, bucket: dict[str, list[float]], key: str, window: int, now: float):
        bucket.setdefault(key, [])
        bucket[key] = [t for t in bucket[key] if now - t < window]

    def check(self, api_key: str, per_minute: int, per_month: int) -> None:
        now = time.time()
        self._prune(self.minute, api_key, 60, now)
        self._prune(self.month, api_key, MONTH_SECONDS, now)
        if len(self.minute[api_key]) >= per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
        if len(self.month[api_key]) >= per_month:
            raise HTTPException(status_code=429, detail="Monthly quota exceeded. Upgrade your plan.")
        self.minute[api_key].append(now)
        self.month[api_key].append(now)

    def remaining(self, api_key: str, per_minute: int, per_month: int) -> dict:
        now = time.time()
        self._prune(self.minute, api_key, 60, now)
        self._prune(self.month, api_key, MONTH_SECONDS, now)
        return {
            "per_minute_remaining": max(0, per_minute - len(self.minute[api_key])),
            "per_month_remaining": max(0, per_month - len(self.month[api_key])),
        }


limiter = RateLimiter()


def require_key(
    x_api_key: str = Header(None),
    x_rapidapi_proxy_secret: str = Header(None),
) -> str:
    secret = os.environ.get("RAPIDAPI_PROXY_SECRET")
    if secret and x_rapidapi_proxy_secret == secret:
        return "rapidapi"
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-API-Key header. Request a key to get started.",
        )
    tier, per_minute, per_month = API_KEYS[x_api_key]
    limiter.check(x_api_key, per_minute, per_month)
    return x_api_key


@app.get("/")
def root():
    return {
        "name": "WebClean API",
        "usage": 'GET /api/extract?url=https://example.com  with header "X-API-Key: demo-free"',
        "interactive_docs": "/docs",
        "test_your_quota": "/api/quota",
    }


@app.get("/api/extract")
def extract(
    api_key: str = Depends(require_key),
    url: str = Query(..., description="The messy webpage URL to clean up"),
):
    try:
        return scrape_url(url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/quota")
def quota(api_key: str = Depends(require_key)):
    if api_key == "rapidapi":
        return {"tier": "rapidapi", "limits": {"per_minute": "unlimited", "per_month": "billed by RapidAPI"}}
    tier, per_minute, per_month = API_KEYS[api_key]
    remaining = limiter.remaining(api_key, per_minute, per_month)
    return {"tier": tier, "limits": {"per_minute": per_minute, "per_month": per_month}, **remaining}
