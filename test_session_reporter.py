#!/usr/bin/env python3
"""
Test script for session reporting functionality.
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.session_reporter import SessionReporter

def test_session_reporter():
    """Test the session reporting functionality."""
    
    print("🧪 Testing Session Reporter")
    print("=" * 50)
    
    # Create a session reporter
    reporter = SessionReporter()
    print(f"📊 Started session: {reporter.session_id}")
    
    # Simulate some scraping attempts
    print("\n🔄 Simulating scraping attempts...")
    
    # Successful attempts
    reporter.record_attempt(
        url="https://blockbeats.com/article1",
        source="BlockBeats",
        success=True,
        title="Test Article 1",
        content_length=500,
        processing_time=0.25
    )
    
    reporter.record_attempt(
        url="https://blockbeats.com/article2", 
        source="BlockBeats",
        success=True,
        title="Test Article 2",
        content_length=750,
        processing_time=0.18
    )
    
    reporter.record_attempt(
        url="https://jinse.com/article1",
        source="Jinse",
        success=True,
        title="Jinse Article 1",
        content_length=600,
        processing_time=0.32
    )
    
    # Failed attempts
    reporter.record_attempt(
        url="https://blockbeats.com/broken",
        source="BlockBeats", 
        success=False,
        error_message="Could not extract article title",
        processing_time=0.15
    )
    
    reporter.record_attempt(
        url="https://jinse.com/broken",
        source="Jinse",
        success=False,
        error_message="Could not extract article body",
        processing_time=0.12
    )
    
    # Record storage
    reporter.record_storage("BlockBeats", 2)
    reporter.record_storage("Jinse", 1)
    
    # Get current stats
    print("\n📈 Current session stats:")
    current_stats = reporter.get_current_stats()
    for key, value in current_stats.items():
        if key != "sources":
            print(f"  {key}: {value}")
    
    print("\n  Sources:")
    for source, stats in current_stats["sources"].items():
        print(f"    {source}: {stats}")
    
    # Wait a moment to show duration
    time.sleep(1)
    
    # Finalize session
    print("\n🏁 Finalizing session...")
    final_report = reporter.finalize_session()
    
    # Print summary
    reporter.print_summary()
    
    # Check if report file was created
    reports_dir = Path("session_reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob(f"{reporter.session_id}_report.json"))
        if report_files:
            print(f"\n✅ Report file created: {report_files[0]}")
            
            # Show a snippet of the report
            import json
            with open(report_files[0], 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            print("\n📄 Report snippet:")
            print(f"  Session ID: {report_data['session_id']}")
            print(f"  Total attempts: {report_data['summary']['total_attempts']}")
            print(f"  Success rate: {report_data['summary']['success_rate_percent']:.1f}%")
            print(f"  Articles stored: {report_data['summary']['articles_stored']}")
        else:
            print("❌ Report file not found")
    else:
        print("❌ Reports directory not found")
    
    print("\n✅ Session Reporter Test Complete!")

if __name__ == "__main__":
    test_session_reporter()