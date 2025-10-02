"""
Contract tests for Creatives API endpoints.
These tests validate API contracts match the OpenAPI specification.
Tests MUST fail until implementation is complete.
"""
import pytest
from fastapi.testclient import TestClient


class TestCreativesAPI:
    """Contract tests for /creatives endpoints"""
    
    def test_list_creatives_returns_200(self, client: TestClient):
        """GET /creatives returns 200 with array of CreativeWithApproval"""
        response = client.get("/creatives")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_creatives_filtered_by_status(self, client: TestClient, sample_creative_id: str):
        """GET /creatives?status=pending returns pending creatives"""
        response = client.get("/creatives?status=pending")
        assert response.status_code == 200
        
        creatives = response.json()
        for creative in creatives:
            assert "approval" in creative
            approval = creative["approval"]
            assert approval["deployed"] is False
    
    def test_get_creative_returns_200(self, client: TestClient, sample_creative_id: str):
        """GET /creatives/{creative_id} returns 200 with CreativeWithApproval schema"""
        response = client.get(f"/creatives/{sample_creative_id}")
        assert response.status_code == 200
        
        creative = response.json()
        assert creative["id"] == sample_creative_id
        assert "file_path" in creative
        assert "approval" in creative
        assert "creative_approved" in creative["approval"]
        assert "regional_approved" in creative["approval"]
        assert "deployed" in creative["approval"]
    
    def test_get_nonexistent_creative_returns_404(self, client: TestClient):
        """GET /creatives/{invalid_id} returns 404"""
        response = client.get("/creatives/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
    
    def test_regenerate_creative_returns_200(self, client: TestClient, sample_creative_id: str):
        """POST /creatives/{creative_id}/regenerate returns 200 with updated Creative"""
        # Get original
        original = client.get(f"/creatives/{sample_creative_id}").json()
        original_path = original["file_path"]
        
        # Regenerate
        response = client.post(f"/creatives/{sample_creative_id}/regenerate")
        assert response.status_code == 200
        
        regenerated = response.json()
        assert regenerated["id"] == sample_creative_id
        assert regenerated["generation_count"] == 2
        assert regenerated["file_path"] != original_path
    
    def test_approve_creative_returns_200(self, client: TestClient, sample_creative_id: str):
        """POST /creatives/{creative_id}/approve-creative returns 200 with updated Approval"""
        response = client.post(f"/creatives/{sample_creative_id}/approve-creative")
        assert response.status_code == 200
        
        approval = response.json()
        assert approval["creative_approved"] is True
        assert "creative_approved_at" in approval
        assert approval["regional_approved"] is False  # Not approved yet
        assert approval["deployed"] is False
    
    def test_approve_regional_returns_200(self, client: TestClient, sample_creative_id: str):
        """POST /creatives/{creative_id}/approve-regional returns 200 with updated Approval"""
        response = client.post(f"/creatives/{sample_creative_id}/approve-regional")
        assert response.status_code == 200
        
        approval = response.json()
        assert approval["regional_approved"] is True
        assert "regional_approved_at" in approval
    
    def test_deploy_without_approvals_returns_400(self, client: TestClient, sample_creative_id: str):
        """POST /creatives/{creative_id}/deploy without approvals returns 400"""
        response = client.post(f"/creatives/{sample_creative_id}/deploy")
        assert response.status_code == 400
    
    def test_deploy_with_both_approvals_returns_200(self, client: TestClient, sample_creative_id: str):
        """POST /creatives/{creative_id}/deploy with both approvals returns 200"""
        # Grant both approvals
        client.post(f"/creatives/{sample_creative_id}/approve-creative")
        client.post(f"/creatives/{sample_creative_id}/approve-regional")
        
        # Deploy
        response = client.post(f"/creatives/{sample_creative_id}/deploy")
        assert response.status_code == 200
        
        approval = response.json()
        assert approval["deployed"] is True
        assert "deployed_at" in approval
    
    def test_deploy_already_deployed_returns_400(self, client: TestClient):
        """POST /creatives/{deployed_id}/deploy returns 400 if already deployed"""
        # Create, approve, and deploy creative
        creative_id = self._create_and_deploy_creative(client)
        
        # Try to deploy again
        response = client.post(f"/creatives/{creative_id}/deploy")
        assert response.status_code == 400
    
    def _create_and_deploy_creative(self, client: TestClient) -> str:
        """Helper to create and fully deploy a creative"""
        # Create brief
        data = {
            "content": "Test brief",
            "campaign_message": "Test",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=data).json()
        
        # Execute to get idea
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        
        # Generate creative
        creative = client.post(f"/ideas/{ideas[0]['id']}/generate-creative").json()
        
        # Approve and deploy
        client.post(f"/creatives/{creative['id']}/approve-creative")
        client.post(f"/creatives/{creative['id']}/approve-regional")
        client.post(f"/creatives/{creative['id']}/deploy")
        
        return creative["id"]


@pytest.fixture
def sample_creative_id(client: TestClient) -> str:
    """Create a sample creative and return its ID"""
    # Create brief
    data = {
        "content": "Test brief for creative",
        "campaign_message": "Test Campaign",
        "regions": '["US"]',
        "demographics": '["18-25"]'
    }
    brief = client.post("/briefs", data=data).json()
    
    # Execute to get ideas
    ideas = client.post(f"/briefs/{brief['id']}/execute").json()
    
    # Generate creative
    creative = client.post(f"/ideas/{ideas[0]['id']}/generate-creative").json()
    
    return creative["id"]
