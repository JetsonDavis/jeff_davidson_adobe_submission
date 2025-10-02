"""
Integration Test: Scenario 8 - Regenerate Creative
Maps to quickstart.md Scenario 8
"""
import pytest
from fastapi.testclient import TestClient


class TestScenario8RegenerateCreative:
    """
    Test creative regeneration and approval reset.
    """
    
    def test_regenerate_creative_resets_approvals(self, client: TestClient):
        """
        Given: Creative with some or all approvals
        When: Manager clicks regenerate
        Then: New creative generated, approval status reset, must re-approve
        """
        # Step 1: Create and approve creative
        creative_id = self._create_test_creative(client)
        
        # Grant both approvals
        client.post(f"/creatives/{creative_id}/approve-creative")
        client.post(f"/creatives/{creative_id}/approve-regional")
        
        # Verify approved
        creative_before = client.get(f"/creatives/{creative_id}").json()
        original_file_path = creative_before["file_path"]
        approval_before = creative_before["approval"]
        assert approval_before["creative_approved"] is True
        assert approval_before["regional_approved"] is True
        assert creative_before["generation_count"] == 1
        
        # Step 2: Regenerate creative
        regenerate_response = client.post(f"/creatives/{creative_id}/regenerate")
        assert regenerate_response.status_code == 200
        
        regenerated = regenerate_response.json()
        
        # Step 3: Verify new creative generated
        assert regenerated["id"] == creative_id  # Same ID
        assert regenerated["generation_count"] == 2  # Incremented
        assert regenerated["file_path"] != original_file_path  # New file
        assert "updated_at" in regenerated
        
        # Step 4: Verify approvals reset
        creative_after = client.get(f"/creatives/{creative_id}").json()
        approval_after = creative_after["approval"]
        assert approval_after["creative_approved"] is False, "Creative approval should reset"
        assert approval_after["regional_approved"] is False, "Regional approval should reset"
        assert approval_after["deployed"] is False
        
        # Step 5: Verify must re-approve before deploying
        deploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_response.status_code == 400, "Should not deploy without re-approval"
    
    def test_regenerate_idea_updates_content(self, client: TestClient):
        """
        Test regenerating an idea (from Scenario 3)
        """
        # Create brief and execute
        brief_data = {
            "content": "Test product for regeneration",
            "campaign_message": "Test",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=brief_data).json()
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        idea_id = ideas[0]["id"]
        
        # Get original idea
        original_idea = client.get(f"/ideas/{idea_id}").json()
        original_content = original_idea["content"]
        assert original_idea["generation_count"] == 1
        
        # Regenerate idea
        regenerate_response = client.post(f"/ideas/{idea_id}/regenerate")
        assert regenerate_response.status_code == 200
        
        new_idea = regenerate_response.json()
        
        # Verify idea updated
        assert new_idea["id"] == idea_id
        assert new_idea["generation_count"] == 2
        assert new_idea["content"] != original_content  # New content
        assert "updated_at" in new_idea
    
    def test_regenerate_creative_multiple_times(self, client: TestClient):
        """
        Verify creative can be regenerated multiple times
        """
        creative_id = self._create_test_creative(client)
        
        # Regenerate 3 times
        for expected_count in [2, 3, 4]:
            response = client.post(f"/creatives/{creative_id}/regenerate")
            assert response.status_code == 200
            
            creative = response.json()
            assert creative["generation_count"] == expected_count
    
    def test_regenerate_preserves_idea_reference(self, client: TestClient):
        """
        Verify regenerating creative keeps same idea_id
        """
        # Create creative
        brief_data = {
            "content": "Test",
            "campaign_message": "Test",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=brief_data).json()
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        idea_id = ideas[0]["id"]
        creative = client.post(f"/ideas/{idea_id}/generate-creative").json()
        
        # Regenerate
        regenerated = client.post(f"/creatives/{creative['id']}/regenerate").json()
        
        # Verify idea_id unchanged
        assert regenerated["idea_id"] == idea_id
    
    def test_regenerate_nonexistent_creative_returns_404(self, client: TestClient):
        """Test error handling for regenerating non-existent creative"""
        response = client.post("/creatives/00000000-0000-0000-0000-000000000000/regenerate")
        assert response.status_code == 404
    
    def _create_test_creative(self, client: TestClient) -> str:
        """Helper to create a creative for testing"""
        brief_data = {
            "content": "Test product",
            "campaign_message": "Test",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=brief_data).json()
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        creative = client.post(f"/ideas/{ideas[0]['id']}/generate-creative").json()
        return creative["id"]
