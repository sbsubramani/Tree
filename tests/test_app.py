import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory `activities` dict before/after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "tester1@mergington.edu"
    activity = "Chess Club"

    # Ensure email is not already present
    for a in activities.values():
        assert email not in a["participants"]

    # Sign up
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(signup_url)
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Attempt to sign the same email up for a different activity -> should fail
    other = "Programming Class"
    r2 = client.post(f"/activities/{quote(other)}/signup?email={quote(email)}")
    assert r2.status_code == 400

    # Unregister the participant
    delete_url = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    r3 = client.delete(delete_url)
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant():
    email = "noone@mergington.edu"
    activity = "Chess Club"
    delete_url = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    r = client.delete(delete_url)
    assert r.status_code == 404
