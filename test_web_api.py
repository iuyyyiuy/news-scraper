"""
Test script for the web API endpoints.
"""
import asyncio
from datetime import date
from scraper.web_api import app, session_manager
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "active_sessions" in data
    print("✓ Health check passed")


def test_scrape_validation():
    """Test scrape request validation."""
    print("\nTesting scrape request validation...")
    
    # Test with invalid date range
    response = client.post("/api/scrape", json={
        "start_date": "2025-11-13",
        "end_date": "2025-11-01",  # Before start date
        "keywords": ["test"]
    })
    assert response.status_code == 422  # Validation error
    print("✓ Date range validation works")
    
    # Test with empty keywords
    response = client.post("/api/scrape", json={
        "start_date": "2025-11-01",
        "end_date": "2025-11-13",
        "keywords": []
    })
    assert response.status_code == 422  # Validation error
    print("✓ Keywords validation works")


def test_scrape_start():
    """Test starting a scrape session."""
    print("\nTesting scrape session creation...")
    
    response = client.post("/api/scrape", json={
        "start_date": "2025-11-01",
        "end_date": "2025-11-13",
        "keywords": ["crypto", "bitcoin"],
        "max_articles": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "running"
    assert data["message"] == "Scraping session started successfully"
    
    session_id = data["session_id"]
    print(f"✓ Session created: {session_id}")
    
    return session_id


def test_session_status(session_id):
    """Test getting session status."""
    print("\nTesting session status endpoint...")
    
    response = client.get(f"/api/status/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert "status" in data
    assert "articles_found" in data
    assert "articles_scraped" in data
    assert "start_time" in data
    assert "keywords" in data
    
    print(f"✓ Session status retrieved")
    print(f"  Status: {data['status']}")
    print(f"  Keywords: {data['keywords']}")


def test_session_not_found():
    """Test getting status for non-existent session."""
    print("\nTesting non-existent session...")
    
    response = client.get("/api/status/invalid-session-id")
    assert response.status_code == 404
    print("✓ 404 returned for invalid session")


def test_list_sessions():
    """Test listing all sessions."""
    print("\nTesting list sessions endpoint...")
    
    response = client.get("/api/sessions")
    assert response.status_code == 200
    
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert "active" in data
    assert isinstance(data["sessions"], list)
    
    print(f"✓ Sessions listed")
    print(f"  Total: {data['total']}")
    print(f"  Active: {data['active']}")


def test_cleanup_sessions():
    """Test cleanup endpoint."""
    print("\nTesting cleanup endpoint...")
    
    response = client.delete("/api/sessions/cleanup")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "removed_count" in data
    
    print(f"✓ Cleanup executed")
    print(f"  Removed: {data['removed_count']} session(s)")


def test_download_not_ready():
    """Test download when session is not ready."""
    print("\nTesting download for incomplete session...")
    
    # Create a new session
    response = client.post("/api/scrape", json={
        "start_date": "2025-11-01",
        "end_date": "2025-11-13",
        "keywords": ["test"]
    })
    session_id = response.json()["session_id"]
    
    # Try to download immediately (should fail)
    response = client.get(f"/api/download/{session_id}")
    assert response.status_code == 400
    print("✓ Download blocked for incomplete session")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Web API Test Suite")
    print("=" * 60)
    
    try:
        test_health_check()
        test_scrape_validation()
        session_id = test_scrape_start()
        test_session_status(session_id)
        test_session_not_found()
        test_list_sessions()
        test_cleanup_sessions()
        test_download_not_ready()
        
        print("\n" + "=" * 60)
        print("✓ All API tests passed!")
        print("=" * 60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
