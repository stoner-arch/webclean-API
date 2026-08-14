import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}"
)
HOURS_RE = re.compile(
    r"\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?\s*(?:[-–—]|to)\s*"
    r"\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)",
    re.IGNORECASE,
)

USER_AGENT = "WebCleanBot/0.1"


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Provide a valid http/https URL, e.g. https://example.com")
    return url


def fetch_html(url: str) -> str:
    response = httpx.get(
        url,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=15.0,
    )
    response.raise_for_status()
    if "text/html" not in response.headers.get("content-type", ""):
        raise ValueError("That URL did not return HTML.")
    return response.text


def extract_emails(text: str) -> list[str]:
    return sorted(set(m.lower() for m in EMAIL_RE.findall(text)))


def extract_phones(text: str) -> list[str]:
    return sorted(set(m.strip() for m in PHONE_RE.findall(text)))


def extract_hours(soup) -> list[str]:
    results = []
    for el in soup.find_all(string=re.compile(r"hours", re.IGNORECASE)):
        parent = el.parent
        if parent is None:
            continue
        window = parent.get_text(" ", strip=True)[:500]
        results.extend(HOURS_RE.findall(window))
    return list(dict.fromkeys(results))


def extract_links(soup, base_url: str, limit: int = 20) -> list[str]:
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        if href.startswith(("http://", "https://")):
            links.append(href)
        elif href.startswith("/"):
            links.append(base_url.rstrip("/") + "/" + href.lstrip("/"))
        else:
            links.append(base_url.rstrip("/") + "/" + href)
    return list(dict.fromkeys(links))[:limit]


def scrape_url(url: str) -> dict:
    validate_url(url)
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    meta_description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_description = meta["content"].strip()
    base = urlparse(url)
    return {
        "url": url,
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "meta_description": meta_description,
        "emails": extract_emails(text),
        "phones": extract_phones(text),
        "hours": extract_hours(soup),
        "links": extract_links(soup, f"{base.scheme}://{base.netloc}"),
        "word_count": len(re.findall(r"\S+", text)),
    }
