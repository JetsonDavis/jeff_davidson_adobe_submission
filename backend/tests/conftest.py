"""
Pytest configuration and shared fixtures for backend tests.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """
    Create FastAPI test client.
    This fixture will be implemented once main.py exists.
    """
    # TODO: Import app from src.main once implemented
    # from src.main import app
    # return TestClient(app)
    pytest.fail("FastAPI app not yet implemented. This test should fail.")
