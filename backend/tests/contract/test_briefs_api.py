"""
Contract tests for Briefs API endpoints.
These tests validate API contracts match the OpenAPI specification.
Tests MUST fail until implementation is complete.
"""
import pytest
from fastapi.testclient import TestClient


class TestBriefsAPI:
    """Contract tests for /briefs endpoints"""
    
    def test_list_briefs_returns_200(self, client: TestClient):
        """GET /briefs returns 200 with array of briefs"""
        response = client.get("/briefs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_brief_with_text_returns_201(self, client: TestClient):
        """POST /briefs with text content returns 201 with Brief schema"""
        data = {
            "content": "Test product brief content",
            "campaign_message": "Summer Sale 20% Off",
            "regions": '["US", "EU"]',
            "demographics": '["18-25", "25-35"]'
        }
        response = client.post("/briefs", data=data)
        assert response.status_code == 201
        
        brief = response.json()
        assert "id" in brief
        assert brief["content"] == data["content"]
        assert brief["campaign_message"] == data["campaign_message"]
        assert brief["source_type"] == "text"
        assert "created_at" in brief
    
    def test_create_brief_with_file_returns_201(self, client: TestClient):
        """POST /briefs with file upload returns 201 with Brief schema"""
        files = {"file": ("test.txt", b"Test brief content", "text/plain")}
        data = {
            "campaign_message": "Winter Sale",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        response = client.post("/briefs", data=data, files=files)
        assert response.status_code == 201
        
        brief = response.json()
        assert "id" in brief
        assert brief["source_type"] == "txt"
        assert brief["source_filename"] == "test.txt"
    
    def test_create_brief_missing_required_fields_returns_400(self, client: TestClient):
        """POST /briefs without required fields returns 400"""
        data = {"content": "Test"}  # Missing campaign_message, regions, demographics
        response = client.post("/briefs", data=data)
        assert response.status_code == 400
    
    def test_get_brief_returns_200(self, client: TestClient, sample_brief_id: str):
        """GET /briefs/{brief_id} returns 200 with Brief schema"""
        response = client.get(f"/briefs/{sample_brief_id}")
        assert response.status_code == 200
        
        brief = response.json()
        assert brief["id"] == sample_brief_id
        assert "content" in brief
        assert "campaign_message" in brief
    
    def test_get_nonexistent_brief_returns_404(self, client: TestClient):
        """GET /briefs/{invalid_id} returns 404"""
        response = client.get("/briefs/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
    
    def test_delete_brief_returns_204(self, client: TestClient, sample_brief_id: str):
        """DELETE /briefs/{brief_id} returns 204"""
        response = client.delete(f"/briefs/{sample_brief_id}")
        assert response.status_code == 204
    
    def test_execute_brief_returns_200_with_ideas(self, client: TestClient, sample_brief_id: str):
        """POST /briefs/{brief_id}/execute returns 200 with array of Ideas"""
        response = client.post(f"/briefs/{sample_brief_id}/execute")
        assert response.status_code == 200
        
        ideas = response.json()
        assert isinstance(ideas, list)
        # Brief has 2 regions × 2 demographics = 4 ideas
        assert len(ideas) == 4
        
        for idea in ideas:
            assert "id" in idea
            assert "brief_id" in idea
            assert "region" in idea
            assert "demographic" in idea
            assert "content" in idea
            assert "language_code" in idea
    
    def test_execute_nonexistent_brief_returns_404(self, client: TestClient):
        """POST /briefs/{invalid_id}/execute returns 404"""
        response = client.post("/briefs/00000000-0000-0000-0000-000000000000/execute")
        assert response.status_code == 404


@pytest.fixture
def sample_brief_id(client: TestClient) -> str:
    """Create a sample brief and return its ID"""
    data = {
        "content": "Sample product brief for testing",
        "campaign_message": "Test Campaign",
        "regions": '["US", "EU"]',
        "demographics": '["18-25", "25-35"]'
    }
    response = client.post("/briefs", data=data)
    return response.json()["id"]
