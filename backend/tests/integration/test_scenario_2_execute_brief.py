"""
Integration Test: Scenario 2 - Execute Brief to Generate Ideas
Maps to quickstart.md Scenario 2
"""
import pytest
from fastapi.testclient import TestClient


class TestScenario2ExecuteBrief:
    """
    Test the LLM integration and idea generation workflow.
    """
    
    def test_execute_brief_generates_ideas(self, client: TestClient):
        """
        Given: Brief with regions and demographics
        When: Manager clicks Execute button
        Then: System generates one idea per region/demographic combination
        """
        # Step 1: Create brief with multiple regions and demographics
        brief_data = {
            "content": "Product: Smart Watch\nFeatures: Health tracking, notifications",
            "campaign_message": "Limited Time Offer",
            "regions": '["US", "EU", "APAC"]',
            "demographics": '["18-25", "25-35"]'
        }
        
        brief_response = client.post("/briefs", data=brief_data)
        brief_id = brief_response.json()["id"]
        
        # Step 2: Execute brief to generate ideas
        execute_response = client.post(f"/briefs/{brief_id}/execute")
        assert execute_response.status_code == 200, f"Expected 200, got {execute_response.status_code}"
        
        ideas = execute_response.json()
        
        # Step 3: Verify correct number of ideas (3 regions × 2 demographics = 6 ideas)
        assert isinstance(ideas, list)
        assert len(ideas) == 6, f"Expected 6 ideas, got {len(ideas)}"
        
        # Step 4: Verify each idea has required fields
        regions_found = set()
        demographics_found = set()
        
        for idea in ideas:
            assert "id" in idea
            assert "brief_id" in idea
            assert idea["brief_id"] == brief_id
            assert "region" in idea
            assert "demographic" in idea
            assert "content" in idea
            assert "language_code" in idea
            assert "generation_count" in idea
            assert idea["generation_count"] == 1
            
            regions_found.add(idea["region"])
            demographics_found.add(idea["demographic"])
        
        # Step 5: Verify all regions and demographics are covered
        assert regions_found == {"US", "EU", "APAC"}
        assert demographics_found == {"18-25", "25-35"}
    
    def test_execute_brief_preserves_brief_and_assets(self, client: TestClient):
        """
        Verify that executing a brief doesn't affect original brief or assets
        """
        # Create brief
        brief_data = {
            "content": "Test brief content",
            "campaign_message": "Test",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        brief_response = client.post("/briefs", data=brief_data)
        brief_id = brief_response.json()["id"]
        
        # Upload asset
        files = {"file": ("test.jpg", b"test", "image/jpeg")}
        asset_response = client.post("/assets/brand", files=files)
        asset_id = asset_response.json()["id"]
        
        # Execute brief
        client.post(f"/briefs/{brief_id}/execute")
        
        # Verify brief unchanged
        brief_check = client.get(f"/briefs/{brief_id}").json()
        assert brief_check["content"] == brief_data["content"]
        
        # Verify asset unchanged
        assets = client.get("/assets").json()
        assert any(a["id"] == asset_id for a in assets)
    
    def test_execute_nonexistent_brief_returns_404(self, client: TestClient):
        """Test error handling for executing non-existent brief"""
        response = client.post("/briefs/00000000-0000-0000-0000-000000000000/execute")
        assert response.status_code == 404
