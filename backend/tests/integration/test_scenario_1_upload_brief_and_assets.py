"""
Integration Test: Scenario 1 - Upload Brief and Assets
Maps to quickstart.md Scenario 1
"""
import pytest
from fastapi.testclient import TestClient


class TestScenario1UploadBriefAndAssets:
    """
    Test the complete workflow for uploading product briefs and assets.
    This test validates file upload, storage, and display functionality.
    """
    
    def test_upload_brief_document_and_assets(self, client: TestClient):
        """
        Given: Marketing manager has product information
        When: They upload brief document and associated assets
        Then: System stores all materials and displays thumbnails with delete options
        """
        # Step 1: Upload product brief as text
        brief_data = {
            "content": "Product: Premium Coffee Maker\nTarget: Coffee enthusiasts\nFeatures: Smart brewing",
            "campaign_message": "Summer Sale - 20% Off!",
            "regions": '["US", "EU", "APAC"]',
            "demographics": '["18-25", "25-35"]'
        }
        
        brief_response = client.post("/briefs", data=brief_data)
        assert brief_response.status_code == 201, f"Expected 201, got {brief_response.status_code}"
        
        brief = brief_response.json()
        assert "id" in brief
        assert brief["content"] == brief_data["content"]
        assert brief["campaign_message"] == brief_data["campaign_message"]
        brief_id = brief["id"]
        
        # Step 2: Upload brand asset (logo)
        brand_file = {"file": ("logo.jpg", b"fake jpg content for brand logo", "image/jpeg")}
        brand_response = client.post("/assets/brand", files=brand_file)
        assert brand_response.status_code == 201
        
        brand_asset = brand_response.json()
        assert brand_asset["asset_type"] == "brand"
        assert brand_asset["filename"] == "logo.jpg"
        assert "file_path" in brand_asset
        
        # Step 3: Upload product asset (product image)
        product_file = {"file": ("product.jpg", b"fake jpg content for product", "image/jpeg")}
        product_response = client.post("/assets/product", files=product_file)
        assert product_response.status_code == 201
        
        product_asset = product_response.json()
        assert product_asset["asset_type"] == "product"
        assert product_asset["filename"] == "product.jpg"
        
        # Step 4: Verify assets can be listed
        assets_response = client.get("/assets")
        assert assets_response.status_code == 200
        
        assets = assets_response.json()
        assert len(assets) >= 2
        asset_ids = [a["id"] for a in assets]
        assert brand_asset["id"] in asset_ids
        assert product_asset["id"] in asset_ids
        
        # Step 5: Verify brief can be retrieved
        get_brief_response = client.get(f"/briefs/{brief_id}")
        assert get_brief_response.status_code == 200
        
        retrieved_brief = get_brief_response.json()
        assert retrieved_brief["id"] == brief_id
        assert retrieved_brief["content"] == brief_data["content"]
    
    def test_upload_brief_from_file(self, client: TestClient):
        """Test uploading brief from TXT file instead of text input"""
        files = {"file": ("brief.txt", b"Product brief from file", "text/plain")}
        data = {
            "campaign_message": "Test Campaign",
            "regions": '["US"]',
            "demographics": '["18-25"]'
        }
        
        response = client.post("/briefs", data=data, files=files)
        assert response.status_code == 201
        
        brief = response.json()
        assert brief["source_type"] == "txt"
        assert brief["source_filename"] == "brief.txt"
        assert "Product brief from file" in brief["content"]
    
    def test_delete_asset(self, client: TestClient):
        """Test deleting an uploaded asset"""
        # Upload asset
        files = {"file": ("test.jpg", b"test content", "image/jpeg")}
        upload_response = client.post("/assets/brand", files=files)
        asset_id = upload_response.json()["id"]
        
        # Delete asset
        delete_response = client.delete(f"/assets/{asset_id}")
        assert delete_response.status_code == 204
        
        # Verify asset is gone
        get_response = client.get("/assets")
        assets = get_response.json()
        asset_ids = [a["id"] for a in assets]
        assert asset_id not in asset_ids
