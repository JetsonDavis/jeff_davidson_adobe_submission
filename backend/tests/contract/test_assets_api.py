"""
Contract tests for Assets API endpoints.
These tests validate API contracts match the OpenAPI specification.
Tests MUST fail until implementation is complete.
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO


class TestAssetsAPI:
    """Contract tests for /assets endpoints"""
    
    def test_upload_brand_asset_returns_201(self, client: TestClient):
        """POST /assets/brand returns 201 with Asset schema"""
        # Create mock JPG file
        files = {"file": ("logo.jpg", b"fake jpg content", "image/jpeg")}
        response = client.post("/assets/brand", files=files)
        assert response.status_code == 201
        
        asset = response.json()
        assert "id" in asset
        assert asset["asset_type"] == "brand"
        assert asset["filename"] == "logo.jpg"
        assert asset["mime_type"] == "image/jpeg"
        assert "file_path" in asset
        assert "file_size" in asset
        assert "created_at" in asset
    
    def test_upload_product_asset_returns_201(self, client: TestClient):
        """POST /assets/product returns 201 with Asset schema"""
        files = {"file": ("product.jpg", b"fake jpg content", "image/jpeg")}
        response = client.post("/assets/product", files=files)
        assert response.status_code == 201
        
        asset = response.json()
        assert asset["asset_type"] == "product"
        assert asset["filename"] == "product.jpg"
    
    def test_upload_invalid_file_type_returns_400(self, client: TestClient):
        """POST /assets/brand with non-JPG returns 400"""
        files = {"file": ("doc.pdf", b"pdf content", "application/pdf")}
        response = client.post("/assets/brand", files=files)
        assert response.status_code == 400
    
    def test_upload_oversized_file_returns_400(self, client: TestClient):
        """POST /assets/brand with file >10MB returns 400"""
        # Create 11MB file
        large_content = b"x" * (11 * 1024 * 1024)
        files = {"file": ("large.jpg", large_content, "image/jpeg")}
        response = client.post("/assets/brand", files=files)
        assert response.status_code == 400
    
    def test_list_assets_returns_200(self, client: TestClient):
        """GET /assets returns 200 with array of Assets"""
        response = client.get("/assets")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_assets_filtered_by_type_returns_200(self, client: TestClient, sample_brand_asset_id: str):
        """GET /assets?asset_type=brand returns only brand assets"""
        response = client.get("/assets?asset_type=brand")
        assert response.status_code == 200
        
        assets = response.json()
        assert all(a["asset_type"] == "brand" for a in assets)
    
    def test_delete_asset_returns_204(self, client: TestClient, sample_brand_asset_id: str):
        """DELETE /assets/{asset_id} returns 204"""
        response = client.delete(f"/assets/{sample_brand_asset_id}")
        assert response.status_code == 204
    
    def test_delete_nonexistent_asset_returns_404(self, client: TestClient):
        """DELETE /assets/{invalid_id} returns 404"""
        response = client.delete("/assets/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


@pytest.fixture
def sample_brand_asset_id(client: TestClient) -> str:
    """Create a sample brand asset and return its ID"""
    files = {"file": ("test_logo.jpg", b"test jpg", "image/jpeg")}
    response = client.post("/assets/brand", files=files)
    return response.json()["id"]
