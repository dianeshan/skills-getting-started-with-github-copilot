import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app


@pytest.fixture
def client():
    """Return a synchronous FastAPI TestClient."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Snapshot in-memory activities before each test and restore after.

    Prevents mutations in one test from bleeding into another.
    """
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)
