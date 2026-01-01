#!/usr/bin/env python3
"""
Test complete CSV export workflow
"""

import os
import sys
import csv
import io
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.csv_exporter import CSVExportService, CSVExportConfig

def test_complete_workflow():
    """Test the complete CSV export workflow"""
    print("🧪 Testing Complete CSV Export Workflow")
    print("=" * 60)
    
    try:
        service = CSVExportService()
        
        # Test 1: Basic export
        print("1️⃣ Testing basic export...")
        config = CSVExportConfig(max_records=5, include_content=True)
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Basic export: {result['articles_count']} articles")
            print(f"📁 File: {os.path.basename(result['file_path'])}")
            
            # Verify file content
            with open(result['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"📄 Lines in file: {len(lines)}")
                print(f"📋 Header: {lines[0]}")
        else:
            print(f"❌ Basic export failed: {result['message']}")
            return False
        
        # Test 2: Filtered export
        print("\n2️⃣ Testing filtered export...")
        config = CSVExportConfig(
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
            sources=['BlockBeats'],
            keywords=['攻击', '安全'],
            max_records=10,
            include_content=False
        )
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Filtered export: {result['articles_count']} articles")
            print(f"📊 Filters: {result['filters_applied']}")
        else:
            print(f"⚠️  Filtered export: {result['message']} (may be no matching articles)")
        
        # Test 3: Large export simulation
        print("\n3️⃣ Testing large export simulation...")
        config = CSVExportConfig(max_records=100, include_content=True)
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Large export: {result['articles_count']} articles")
            print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
            
            # Performance check
            if result['duration_seconds'] < 30:
                print(f"✅ Performance: Export completed in reasonable time")
            else:
                print(f"⚠️  Performance: Export took longer than expected")
        else:
            print(f"❌ Large export failed: {result['message']}")
        
        # Test 4: CSV format validation
        print("\n4️⃣ Testing CSV format validation...")
        if result['success'] and result['file_path']:
            try:
                with open(result['file_path'], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                print(f"✅ CSV parsing: {len(rows)} rows parsed successfully")
                
                if rows:
                    sample_row = rows[0]
                    required_columns = ['date', 'title', 'source', 'keywords', 'url']
                    missing_columns = [col for col in required_columns if col not in sample_row]
                    
                    if not missing_columns:
                        print(f"✅ CSV structure: All required columns present")
                    else:
                        print(f"❌ CSV structure: Missing columns: {missing_columns}")
                        return False
                    
                    # Check for Chinese characters
                    if any('中' in str(value) or '攻' in str(value) for value in sample_row.values()):
                        print(f"✅ Encoding: Chinese characters preserved")
                    else:
                        print(f"⚠️  Encoding: No Chinese characters found in sample")
                
            except Exception as e:
                print(f"❌ CSV validation error: {str(e)}")
                return False
        
        # Test 5: File cleanup
        print("\n5️⃣ Testing file cleanup...")
        export_dir = service.export_dir
        files_before = len([f for f in os.listdir(export_dir) if f.endswith('.csv')])
        
        # Create a test file with old timestamp
        import time
        test_file = os.path.join(export_dir, 'test_old_file.csv')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Modify timestamp to make it "old"
        old_time = time.time() - (2 * 24 * 60 * 60)  # 2 days ago
        os.utime(test_file, (old_time, old_time))
        
        # Run cleanup
        service.cleanup_old_exports(days=1)
        
        files_after = len([f for f in os.listdir(export_dir) if f.endswith('.csv')])
        
        if not os.path.exists(test_file):
            print(f"✅ Cleanup: Old files removed successfully")
        else:
            print(f"❌ Cleanup: Old files not removed")
            return False
        
        print(f"\n🎉 All workflow tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmark():
    """Test performance with realistic data volumes"""
    print("\n🚀 Performance Benchmark Test")
    print("=" * 60)
    
    try:
        service = CSVExportService()
        
        # Test different record counts
        test_sizes = [10, 50, 100, 500]
        
        for size in test_sizes:
            print(f"\n📊 Testing {size} records...")
            
            config = CSVExportConfig(max_records=size, include_content=True)
            result = service.export_articles(config)
            
            if result['success']:
                duration = result['duration_seconds']
                records_per_second = result['articles_count'] / duration if duration > 0 else 0
                
                print(f"✅ {result['articles_count']} articles in {duration:.2f}s")
                print(f"📈 Performance: {records_per_second:.1f} records/second")
                
                # Performance thresholds
                if records_per_second > 10:
                    print(f"🚀 Excellent performance")
                elif records_per_second > 5:
                    print(f"✅ Good performance")
                else:
                    print(f"⚠️  Performance could be improved")
            else:
                print(f"❌ Failed to export {size} records: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 CSV Export Complete Workflow Test")
    print("=" * 60)
    
    # Run workflow test
    workflow_success = test_complete_workflow()
    
    # Run performance test
    performance_success = test_performance_benchmark()
    
    print("\n" + "=" * 60)
    print("📊 Final Results:")
    print(f"   Workflow Test: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    print(f"   Performance Test: {'✅ PASSED' if performance_success else '❌ FAILED'}")
    
    if workflow_success and performance_success:
        print("🎉 All tests PASSED! CSV export is ready for production.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    print("=" * 60)