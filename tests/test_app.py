import os
import sys
import importlib

import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import app as app_module


@pytest.fixture(autouse=True)
def reload_app():
    importlib.reload(app_module)
    yield


def test_get_activities():
    client = TestClient(app_module.app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app_module.app)
    activity = "Tennis Club"
    email = "test.user@mergington.edu"

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # ensure participant present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # unregister
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # ensure removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants


def test_signup_duplicate_returns_400():
    client = TestClient(app_module.app)
    activity = "Tennis Club"
    # existing participant from initial data
    existing = "alex@mergington.edu"
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_not_signed_returns_400():
    client = TestClient(app_module.app)
    activity = "Tennis Club"
    not_signed = "nobody@mergington.edu"
    resp = client.delete(f"/activities/{activity}/signup?email={not_signed}")
    assert resp.status_code == 400


def test_activity_not_found_returns_404():
    client = TestClient(app_module.app)
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404
    resp = client.delete("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404
