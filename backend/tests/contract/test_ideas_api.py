"""
Contract tests for Ideas API endpoints.
These tests validate API contracts match the OpenAPI specification.
Tests MUST fail until implementation is complete.
"""
import pytest
from fastapi.testclient import TestClient


class TestIdeasAPI:
    """Contract tests for /ideas endpoints"""
    
    def test_get_idea_returns_200(self, client: TestClient, sample_idea_id: str):
        """GET /ideas/{idea_id} returns 200 with Idea schema"""
        response = client.get(f"/ideas/{sample_idea_id}")
        assert response.status_code == 200
        
        idea = response.json()
        assert idea["id"] == sample_idea_id
        assert "brief_id" in idea
        assert "region" in idea
        assert "demographic" in idea
        assert "content" in idea
        assert "language_code" in idea
        assert "generation_count" in idea
        assert idea["generation_count"] == 1
    
    def test_get_nonexistent_idea_returns_404(self, client: TestClient):
        """GET /ideas/{invalid_id} returns 404"""
        response = client.get("/ideas/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
    
    def test_regenerate_idea_returns_200(self, client: TestClient, sample_idea_id: str):
        """POST /ideas/{idea_id}/regenerate returns 200 with updated Idea"""
        # Get original content
        original = client.get(f"/ideas/{sample_idea_id}").json()
        original_content = original["content"]
        
        # Regenerate
        response = client.post(f"/ideas/{sample_idea_id}/regenerate")
        assert response.status_code == 200
        
        regenerated = response.json()
        assert regenerated["id"] == sample_idea_id
        assert regenerated["generation_count"] == 2
        assert regenerated["content"] != original_content  # New content
        assert "updated_at" in regenerated
    
    def test_regenerate_nonexistent_idea_returns_404(self, client: TestClient):
        """POST /ideas/{invalid_id}/regenerate returns 404"""
        response = client.post("/ideas/00000000-0000-0000-0000-000000000000/regenerate")
        assert response.status_code == 404
    
    def test_generate_creative_returns_201(self, client: TestClient, sample_idea_id: str):
        """POST /ideas/{idea_id}/generate-creative returns 201 with Creative schema"""
        response = client.post(f"/ideas/{sample_idea_id}/generate-creative")
        assert response.status_code == 201
        
        creative = response.json()
        assert "id" in creative
        assert creative["idea_id"] == sample_idea_id
        assert "file_path" in creative
        assert "mime_type" in creative
        assert "file_size" in creative
        assert "generation_count" in creative
        assert creative["generation_count"] == 1
    
    def test_generate_creative_nonexistent_idea_returns_404(self, client: TestClient):
        """POST /ideas/{invalid_id}/generate-creative returns 404"""
        response = client.post("/ideas/00000000-0000-0000-0000-000000000000/generate-creative")
        assert response.status_code == 404


@pytest.fixture
def sample_idea_id(client: TestClient) -> str:
    """Create a sample brief, execute it, and return first idea ID"""
    # Create brief
    data = {
        "content": "Test brief for idea creation",
        "campaign_message": "Test Campaign",
        "regions": '["US"]',
        "demographics": '["18-25"]'
    }
    brief_response = client.post("/briefs", data=data)
    brief_id = brief_response.json()["id"]
    
    # Execute to generate ideas
    execute_response = client.post(f"/briefs/{brief_id}/execute")
    ideas = execute_response.json()
    return ideas[0]["id"]
