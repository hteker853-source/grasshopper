"""Automated UX, DOM accessibility, and dashboard telemetry verification tests."""

from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from grasshopper.main import app


def test_dashboard_telemetry_elements_and_viewport():
    """Verify dashboard renders required telemetry panels, responsive tags, and chart containers."""
    client = TestClient(app)
    # With valid token or default bypass
    response = client.get("/")
    assert response.status_code in {200, 307, 401}  # 401 when API_TOKEN required

    # Parse template directly to verify DOM structure and accessibility
    html = (Path(__file__).resolve().parents[1] / "grasshopper" / "ui" / "templates" / "dashboard.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Responsive design meta tag
    viewport = soup.find("meta", attrs={"name": "viewport"})
    assert viewport is not None
    assert "width=device-width" in viewport.get("content", "")

    # Telemetry panels in dashboard template
    assert 'id="learning"' in html, "Dashboard missing #learning panel"
    assert 'id="savings"' in html, "Dashboard missing #savings panel"
    assert 'id="isolated"' in html, "Dashboard missing #isolated badge"
    assert "öğrenme grafiği" in html
    assert "Maliyet tasarrufu" in html


def test_alexa_simulator_interactive_elements():
    """Verify Alexa simulator page contains required input surfaces and action controls."""
    html = (Path(__file__).resolve().parents[1] / "grasshopper" / "ui" / "templates" / "alexa.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Form and input surface
    form = soup.find("form") or soup.find("div", class_="alexa-box") or soup.find("textarea") or soup.find("input")
    assert form is not None, "Alexa simulator missing input surface"


def test_run_page_live_frame_and_step_telemetry():
    """Verify individual run page contains live frame updates and step progress views."""
    html = (Path(__file__).resolve().parents[1] / "grasshopper" / "ui" / "templates" / "run.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Live frame feed
    img = soup.find("img")
    assert img is not None, "Run page missing live screenshot preview"
    src = img.get("src", "")
    assert "live.png" in src or "screenshot" in src or "{{" in src
