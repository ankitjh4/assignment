"""
Integration tests for DRINKOO API endpoints.
Tests full request/response cycles using FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "rag_ready" in data
    
    def test_status_endpoint(self):
        """Test /status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "api_health" in data
        assert "database_health" in data
        assert "rag_ready" in data
    
    def test_version_endpoint(self):
        """Test /version endpoint."""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "api_title" in data


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_signup_success(self):
        """Test successful user signup."""
        response = client.post("/auth/signup", json={
            "username": "testuser123",
            "email": "testuser123@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser123"
    
    def test_signup_invalid_email(self):
        """Test signup with invalid email."""
        response = client.post("/auth/signup", json={
            "username": "testuser",
            "email": "invalidemail",
            "password": "password123"
        })
        
        assert response.status_code == 400
    
    def test_signup_weak_password(self):
        """Test signup with weak password."""
        response = client.post("/auth/signup", json={
            "username": "testuser",
            "email": "testuser@test.com",
            "password": "123"  # Too short
        })
        
        assert response.status_code == 400
    
    def test_signup_short_username(self):
        """Test signup with short username."""
        response = client.post("/auth/signup", json={
            "username": "ab",  # Too short
            "email": "testuser@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
    
    def test_login_success(self):
        """Test successful login."""
        # First signup
        signup_response = client.post("/auth/signup", json={
            "username": "logintest",
            "email": "logintest@test.com",
            "password": "password123"
        })
        assert signup_response.status_code == 200
        
        # Then login
        login_response = client.post("/auth/login", json={
            "username": "logintest",
            "password": "password123"
        })
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "logintest"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401


class TestChatbotEndpoint:
    """Test chatbot endpoint."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        response = client.post("/auth/signup", json={
            "username": "chatbottest",
            "email": "chatbottest@test.com",
            "password": "password123"
        })
        return response.json()["access_token"]
    
    def test_chatbot_requires_auth(self):
        """Test that chatbot endpoint requires authentication."""
        response = client.post("/chatbot/ask", json={
            "message": "What is your favorite drink?"
        })
        
        assert response.status_code == 403
    
    def test_chatbot_ask_with_auth(self, auth_token):
        """Test chatbot with valid authentication."""
        response = client.post(
            "/chatbot/ask",
            json={"message": "What orange juice do you have?"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "query" in data
        assert data["status"] == "success"
    
    def test_chatbot_empty_message(self, auth_token):
        """Test chatbot with empty message."""
        response = client.post(
            "/chatbot/ask",
            json={"message": ""},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
    
    def test_chatbot_history_endpoint(self, auth_token):
        """Test chat history endpoint."""
        response = client.get(
            "/chatbot/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "history" in data


class TestUploadEndpoint:
    """Test file upload endpoint."""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests."""
        response = client.post("/auth/signup", json={
            "username": "uploadtest",
            "email": "uploadtest@test.com",
            "password": "password123"
        })
        return response.json()["access_token"]
    
    def test_upload_requires_auth(self):
        """Test that upload endpoint requires authentication."""
        response = client.post("/upload/image", files={
            "file": ("test.jpg", b"fake image data", "image/jpeg")
        })
        
        assert response.status_code == 403
    
    def test_upload_valid_image(self, auth_token):
        """Test uploading valid image."""
        response = client.post(
            "/upload/image",
            files={"file": ("test.png", b"fake png data", "image/png")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "filename" in data
        assert "size_bytes" in data
    
    def test_upload_invalid_mime_type(self, auth_token):
        """Test uploading invalid file type."""
        response = client.post(
            "/upload/image",
            files={"file": ("test.txt", b"text content", "text/plain")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
    
    def test_upload_oversized_file(self, auth_token):
        """Test uploading oversized file."""
        # Create a file larger than 5MB
        large_data = b"x" * (6 * 1024 * 1024)  # 6MB
        
        response = client.post(
            "/upload/image",
            files={"file": ("large.jpg", large_data, "image/jpeg")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 413


class TestLogoutEndpoint:
    """Test logout endpoint."""
    
    def test_logout(self):
        """Test logout endpoint."""
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
