"""
Integration Test: Scenario 5-7 - Approval Workflow and Deployment
Maps to quickstart.md Scenarios 5, 6, and 7
"""
import pytest
from fastapi.testclient import TestClient


class TestScenario5ApprovalWorkflow:
    """
    Test the two-stage approval workflow and deployment.
    """
    
    def test_approval_workflow_creative_then_regional(self, client: TestClient):
        """
        Scenario 5: Grant creative approval first, then regional approval
        Given: Creative in approval queue
        When: Creative approval granted, then regional approval granted
        Then: Deploy button becomes active only after both approvals
        """
        # Setup: Create brief, execute, generate creative
        creative_id = self._create_test_creative(client)
        
        # Step 1: Verify deploy button inactive initially
        creative = client.get(f"/creatives/{creative_id}").json()
        approval = creative["approval"]
        assert approval["creative_approved"] is False
        assert approval["regional_approved"] is False
        assert approval["deployed"] is False
        
        # Step 2: Grant creative approval
        creative_approval_response = client.post(f"/creatives/{creative_id}/approve-creative")
        assert creative_approval_response.status_code == 200
        
        approval_after_creative = creative_approval_response.json()
        assert approval_after_creative["creative_approved"] is True
        assert "creative_approved_at" in approval_after_creative
        assert approval_after_creative["regional_approved"] is False
        assert approval_after_creative["deployed"] is False
        
        # Step 3: Verify deploy still not allowed (missing regional approval)
        deploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_response.status_code == 400, "Should not deploy without both approvals"
        
        # Step 4: Grant regional approval
        regional_approval_response = client.post(f"/creatives/{creative_id}/approve-regional")
        assert regional_approval_response.status_code == 200
        
        approval_after_both = regional_approval_response.json()
        assert approval_after_both["creative_approved"] is True
        assert approval_after_both["regional_approved"] is True
        assert "regional_approved_at" in approval_after_both
        assert approval_after_both["deployed"] is False
        
        # Step 5: Now deploy should be allowed
        deploy_success_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_success_response.status_code == 200
        
        final_approval = deploy_success_response.json()
        assert final_approval["deployed"] is True
        assert "deployed_at" in final_approval
    
    def test_approval_workflow_regional_then_creative(self, client: TestClient):
        """
        Scenario 6: Grant regional approval first, then creative approval
        Verifies approval order independence
        """
        creative_id = self._create_test_creative(client)
        
        # Step 1: Grant regional approval first
        regional_response = client.post(f"/creatives/{creative_id}/approve-regional")
        assert regional_response.status_code == 200
        
        approval_after_regional = regional_response.json()
        assert approval_after_regional["regional_approved"] is True
        assert approval_after_regional["creative_approved"] is False
        assert approval_after_regional["deployed"] is False
        
        # Step 2: Verify deploy still not allowed
        deploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_response.status_code == 400
        
        # Step 3: Grant creative approval
        creative_response = client.post(f"/creatives/{creative_id}/approve-creative")
        assert creative_response.status_code == 200
        
        approval_after_both = creative_response.json()
        assert approval_after_both["creative_approved"] is True
        assert approval_after_both["regional_approved"] is True
        
        # Step 4: Now deploy should work
        deploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_response.status_code == 200
        assert deploy_response.json()["deployed"] is True
    
    def test_deploy_shows_deployed_banner(self, client: TestClient):
        """
        Scenario 7: Verify deployed creative shows deployed status
        """
        creative_id = self._create_and_approve_creative(client)
        
        # Deploy
        deploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert deploy_response.status_code == 200
        
        # Verify deployed status persists
        creative = client.get(f"/creatives/{creative_id}").json()
        approval = creative["approval"]
        assert approval["deployed"] is True
        assert approval["deployed_at"] is not None
    
    def test_cannot_redeploy_deployed_creative(self, client: TestClient):
        """
        Verify that already-deployed creative cannot be deployed again
        """
        creative_id = self._create_and_approve_creative(client)
        
        # First deployment
        client.post(f"/creatives/{creative_id}/deploy")
        
        # Attempt second deployment
        redeploy_response = client.post(f"/creatives/{creative_id}/deploy")
        assert redeploy_response.status_code == 400
        
        error = redeploy_response.json()
        assert "already deployed" in error["message"].lower() or "deployed" in error["message"].lower()
    
    def test_filter_creatives_by_status(self, client: TestClient):
        """
        Test filtering creatives in approval queue by status
        """
        # Create multiple creatives with different statuses
        creative1_id = self._create_test_creative(client)  # Pending
        creative2_id = self._create_and_approve_creative(client)  # Approved
        creative3_id = self._create_and_approve_creative(client)
        client.post(f"/creatives/{creative3_id}/deploy")  # Deployed
        
        # Filter by pending
        pending_response = client.get("/creatives?status=pending")
        pending_creatives = pending_response.json()
        assert any(c["id"] == creative1_id for c in pending_creatives)
        
        # Filter by deployed
        deployed_response = client.get("/creatives?status=deployed")
        deployed_creatives = deployed_response.json()
        assert any(c["id"] == creative3_id for c in deployed_creatives)
    
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
    
    def _create_and_approve_creative(self, client: TestClient) -> str:
        """Helper to create and fully approve a creative"""
        creative_id = self._create_test_creative(client)
        client.post(f"/creatives/{creative_id}/approve-creative")
        client.post(f"/creatives/{creative_id}/approve-regional")
        return creative_id
