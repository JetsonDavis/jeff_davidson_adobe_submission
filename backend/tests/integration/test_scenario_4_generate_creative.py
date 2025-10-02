"""
Integration Test: Scenario 4 - Generate Creative with Adobe Firefly
Maps to quickstart.md Scenario 4
"""
import pytest
from fastapi.testclient import TestClient


class TestScenario4GenerateCreative:
    """
    Test Adobe Firefly integration and creative asset generation.
    """
    
    def test_generate_creative_from_idea(self, client: TestClient):
        """
        Given: An idea exists
        When: Manager clicks play button
        Then: Creative is generated with campaign message and branding
        """
        # Step 1: Create brief
        brief_data = {
            "content": "Product: Running Shoes\nTarget: Athletes",
            "campaign_message": "Run Faster, Go Further",
            "regions": '["US"]',
            "demographics": '["25-35"]'
        }
        brief_response = client.post("/briefs", data=brief_data)
        brief_id = brief_response.json()["id"]
        
        # Step 2: Upload brand asset (for colors/logo)
        brand_file = {"file": ("logo.jpg", b"brand logo data", "image/jpeg")}
        client.post("/assets/brand", files=brand_file)
        
        # Step 3: Execute to generate ideas
        execute_response = client.post(f"/briefs/{brief_id}/execute")
        ideas = execute_response.json()
        idea_id = ideas[0]["id"]
        
        # Step 4: Generate creative from idea
        creative_response = client.post(f"/ideas/{idea_id}/generate-creative")
        assert creative_response.status_code == 201, f"Expected 201, got {creative_response.status_code}"
        
        creative = creative_response.json()
        
        # Step 5: Verify creative structure
        assert "id" in creative
        assert creative["idea_id"] == idea_id
        assert "file_path" in creative
        assert "mime_type" in creative
        assert "file_size" in creative
        assert "generation_count" in creative
        assert creative["generation_count"] == 1
        assert "created_at" in creative
    
    def test_creative_appears_in_approval_queue(self, client: TestClient):
        """
        Verify that generated creative appears in approval queue with correct status
        """
        # Setup: Create brief, execute, generate creative
        brief_data = {
            "content": "Test product",
            "campaign_message": "Test Campaign",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=brief_data).json()
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        creative = client.post(f"/ideas/{ideas[0]['id']}/generate-creative").json()
        creative_id = creative["id"]
        
        # Get creatives list (approval queue)
        queue_response = client.get("/creatives")
        assert queue_response.status_code == 200
        
        creatives = queue_response.json()
        assert len(creatives) > 0
        
        # Find our creative in queue
        our_creative = next((c for c in creatives if c["id"] == creative_id), None)
        assert our_creative is not None
        
        # Verify approval structure
        assert "approval" in our_creative
        approval = our_creative["approval"]
        assert approval["creative_approved"] is False
        assert approval["regional_approved"] is False
        assert approval["deployed"] is False
    
    def test_generate_creative_for_nonexistent_idea_returns_404(self, client: TestClient):
        """Test error handling for generating creative from non-existent idea"""
        response = client.post("/ideas/00000000-0000-0000-0000-000000000000/generate-creative")
        assert response.status_code == 404
    
    def test_multiple_creatives_per_brief(self, client: TestClient):
        """
        Test that multiple ideas from same brief can each generate creatives
        """
        # Create brief with multiple region/demographic combinations
        brief_data = {
            "content": "Multi-region product",
            "campaign_message": "Global Campaign",
            "regions": '["US", "EU"]',
            "demographics": '["18-25"]'
        }
        brief = client.post("/briefs", data=brief_data).json()
        ideas = client.post(f"/briefs/{brief['id']}/execute").json()
        
        # Generate creative for each idea
        creatives = []
        for idea in ideas:
            creative = client.post(f"/ideas/{idea['id']}/generate-creative").json()
            creatives.append(creative)
        
        # Verify we got 2 creatives (2 regions × 1 demographic)
        assert len(creatives) == 2
        
        # Verify creatives are distinct
        creative_ids = [c["id"] for c in creatives]
        assert len(set(creative_ids)) == 2  # All unique
