"""
Unit tests for authentication module.
"""
import pytest
from backend.auth import (
    hash_password, verify_password, create_user, authenticate_user,
    create_access_token, verify_token, user_exists, UserCredentials
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test that password is hashed."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_correct_password(self):
        """Test verifying correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test verifying incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestTokenOperations:
    """Test JWT token operations."""
    
    def test_create_access_token(self):
        """Test creating access token."""
        user_id = 1
        username = "testuser"
        
        token, expiry = create_access_token(user_id, username)
        
        assert token is not None
        assert len(token) > 0
        assert expiry is not None
    
    def test_verify_valid_token(self):
        """Test verifying valid token."""
        user_id = 1
        username = "testuser"
        
        token, _ = create_access_token(user_id, username)
        token_data = verify_token(token)
        
        assert token_data is not None
        assert token_data.user_id == user_id
        assert token_data.username == username
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"
        token_data = verify_token(invalid_token)
        
        assert token_data is None


class TestUserOperations:
    """Test user creation and authentication."""
    
    def test_user_operations_integration(self):
        """Test full user signup and login cycle."""
        credentials = UserCredentials(
            username="newuser",
            email="newuser@test.com",
            password="password123"
        )
        
        # Create user
        user = create_user(credentials)
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@test.com"
        
        # Authenticate with correct password
        auth_user = authenticate_user("newuser", "password123")
        assert auth_user is not None
        assert auth_user.id == user.id
        
        # Authenticate with wrong password
        auth_user = authenticate_user("newuser", "wrongpassword")
        assert auth_user is None


class TestUserExistence:
    """Test user existence checking."""
    
    def test_existing_user_duplicate(self):
        """Test that duplicate users cannot be created."""
        credentials1 = UserCredentials(
            username="dupuser",
            email="dupuser@test.com",
            password="password123"
        )
        
        user1 = create_user(credentials1)
        assert user1 is not None
        
        # Try to create duplicate
        user2 = create_user(credentials1)
        assert user2 is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
