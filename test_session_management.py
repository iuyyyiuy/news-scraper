"""
Test script for session management functionality.
"""
from datetime import datetime, timedelta
from scraper.core import SessionManager, Session, SessionStatus, Article, ScrapingResult


def test_session_creation():
    """Test creating a new session."""
    print("Testing session creation...")
    manager = SessionManager(retention_hours=24)
    
    session_id = manager.create_session(
        start_date=datetime(2025, 11, 1),
        end_date=datetime(2025, 11, 13),
        keywords=["crypto", "bitcoin"]
    )
    
    assert session_id is not None
    assert manager.session_exists(session_id)
    
    session = manager.get_session(session_id)
    assert session is not None
    assert session.status == SessionStatus.RUNNING
    assert session.articles_found == 0
    assert session.articles_scraped == 0
    assert session.keywords == ["crypto", "bitcoin"]
    
    print(f"✓ Session created with ID: {session_id}")
    print(f"  Status: {session.status.value}")
    print(f"  Keywords: {session.keywords}")
    return manager, session_id


def test_progress_updates(manager, session_id):
    """Test updating session progress."""
    print("\nTesting progress updates...")
    
    manager.update_progress(session_id, articles_found=10)
    session = manager.get_session(session_id)
    assert session.articles_found == 10
    
    manager.update_progress(session_id, articles_scraped=5)
    session = manager.get_session(session_id)
    assert session.articles_scraped == 5
    
    print(f"✓ Progress updated: {session.articles_found} found, {session.articles_scraped} scraped")


def test_add_articles(manager, session_id):
    """Test adding articles to session."""
    print("\nTesting article addition...")
    
    article = Article(
        url="https://example.com/article1",
        title="Test Article",
        publication_date=datetime.now(),
        author="Test Author",
        body_text="This is a test article about crypto.",
        scraped_at=datetime.now(),
        source_website="example.com",
        matched_keywords=["crypto"]
    )
    
    manager.add_article(session_id, article)
    session = manager.get_session(session_id)
    
    assert len(session.articles) == 1
    assert session.articles[0].title == "Test Article"
    assert session.articles_scraped == 1
    
    print(f"✓ Article added: {article.title}")


def test_complete_session(manager, session_id):
    """Test completing a session."""
    print("\nTesting session completion...")
    
    result = ScrapingResult(
        total_articles_found=10,
        articles_scraped=1,
        articles_failed=0,
        duration_seconds=5.5,
        errors=[]
    )
    
    manager.complete_session(session_id, result)
    session = manager.get_session(session_id)
    
    assert session.status == SessionStatus.COMPLETED
    assert session.end_time is not None
    assert session.csv_ready is True
    assert session.scraping_result is not None
    
    print(f"✓ Session completed")
    print(f"  Status: {session.status.value}")
    print(f"  Duration: {session.duration_seconds:.2f}s")
    print(f"  CSV Ready: {session.csv_ready}")


def test_session_to_dict(manager, session_id):
    """Test converting session to dictionary."""
    print("\nTesting session serialization...")
    
    session = manager.get_session(session_id)
    session_dict = session.to_dict()
    
    assert session_dict["session_id"] == session_id
    assert session_dict["status"] == "completed"
    assert session_dict["csv_ready"] is True
    assert "start_time" in session_dict
    assert "end_time" in session_dict
    
    print("✓ Session serialized to dictionary:")
    print(f"  Session ID: {session_dict['session_id']}")
    print(f"  Status: {session_dict['status']}")
    print(f"  Articles: {session_dict['articles_scraped']}")


def test_fail_session():
    """Test failing a session."""
    print("\nTesting session failure...")
    
    manager = SessionManager()
    session_id = manager.create_session()
    
    manager.fail_session(session_id, "Network error occurred")
    session = manager.get_session(session_id)
    
    assert session.status == SessionStatus.FAILED
    assert session.error_message == "Network error occurred"
    assert session.csv_ready is False
    
    print(f"✓ Session failed with error: {session.error_message}")


def test_cleanup_old_sessions():
    """Test cleaning up old sessions."""
    print("\nTesting session cleanup...")
    
    manager = SessionManager(retention_hours=1)
    
    # Create and complete a session
    session_id = manager.create_session()
    result = ScrapingResult(
        total_articles_found=5,
        articles_scraped=5,
        articles_failed=0,
        duration_seconds=3.0,
        errors=[]
    )
    manager.complete_session(session_id, result)
    
    # Manually set end_time to past
    session = manager.get_session(session_id)
    session.end_time = datetime.now() - timedelta(hours=2)
    
    # Cleanup
    removed = manager.cleanup_old_sessions()
    
    assert removed == 1
    assert not manager.session_exists(session_id)
    
    print(f"✓ Cleaned up {removed} old session(s)")


def test_progress_callback():
    """Test progress callback functionality."""
    print("\nTesting progress callbacks...")
    
    manager = SessionManager()
    session_id = manager.create_session()
    
    callback_called = []
    
    def progress_callback(session):
        callback_called.append(session.articles_found)
    
    manager.register_progress_callback(session_id, progress_callback)
    manager.update_progress(session_id, articles_found=5)
    
    assert len(callback_called) == 1
    assert callback_called[0] == 5
    
    print(f"✓ Callback triggered with articles_found={callback_called[0]}")


def test_concurrent_sessions():
    """Test managing multiple concurrent sessions."""
    print("\nTesting concurrent sessions...")
    
    manager = SessionManager()
    
    session_id1 = manager.create_session(keywords=["bitcoin"])
    session_id2 = manager.create_session(keywords=["ethereum"])
    session_id3 = manager.create_session(keywords=["crypto"])
    
    active_sessions = manager.get_active_sessions()
    assert len(active_sessions) == 3
    
    # Complete one session
    result = ScrapingResult(
        total_articles_found=5,
        articles_scraped=5,
        articles_failed=0,
        duration_seconds=2.0,
        errors=[]
    )
    manager.complete_session(session_id1, result)
    
    active_sessions = manager.get_active_sessions()
    assert len(active_sessions) == 2
    
    all_sessions = manager.get_all_sessions()
    assert len(all_sessions) == 3
    
    print(f"✓ Managing {len(all_sessions)} total sessions")
    print(f"  Active: {len(active_sessions)}")
    print(f"  Completed: {len(all_sessions) - len(active_sessions)}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Session Management Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        manager, session_id = test_session_creation()
        test_progress_updates(manager, session_id)
        test_add_articles(manager, session_id)
        test_complete_session(manager, session_id)
        test_session_to_dict(manager, session_id)
        test_fail_session()
        test_cleanup_old_sessions()
        test_progress_callback()
        test_concurrent_sessions()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
