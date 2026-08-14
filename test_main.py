from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from scraper import extract_emails, extract_hours, extract_phones

client = TestClient(app)

SAMPLE_HTML = """
<html>
  <head>
    <title>Joe's Diner</title>
    <meta name="description" content="Best burgers in town.">
  </head>
  <body>
    <p>Contact us at joe@diner.com or support@diner.com.</p>
    <p>Call (555) 123-4567 or 800-555-0199 today!</p>
    <p>Hours: Monday-Friday 9:00 AM - 5:00 PM</p>
    <a href="/menu">Menu</a>
    <a href="https://example.com">Home</a>
  </body>
</html>
"""


def test_extract_emails():
    assert extract_emails("a@b.com and c@d.org") == ["a@b.com", "c@d.org"]


def test_extract_phones():
    phones = extract_phones("Call (555) 123-4567 or 800-555-0199")
    assert "(555) 123-4567" in phones
    assert "800-555-0199" in phones


def test_extract_hours():
    soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
    hours = extract_hours(soup)
    assert "9:00 AM - 5:00 PM" in hours


def test_extract_endpoint(monkeypatch):
    monkeypatch.setattr("scraper.fetch_html", lambda url: SAMPLE_HTML)
    response = client.get("/api/extract", params={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Joe's Diner"
    assert data["meta_description"] == "Best burgers in town."
    assert "joe@diner.com" in data["emails"]
    assert "https://example.com/menu" in data["links"]
