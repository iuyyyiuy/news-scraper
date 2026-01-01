#!/usr/bin/env python3
"""
Diagnostic script to test the manual update API endpoint.
This script will:
1. Test the manual update API endpoint directly
2. Verify parameter passing and response
3. Check database connection and article storage
4. Identify specific issues with the manual update workflow
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualUpdateDebugger:
    """Debug manual update API endpoint"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self):
        """Test the health check endpoint"""
        print("=" * 60)
        print("TESTING HEALTH CHECK")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            print(f"Health check status: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Database: {health_data.get('database')}")
                print(f"   Environment variables:")
                for key, value in health_data.get('env_vars', {}).items():
                    print(f"     {key}: {value}")
                return True
            else:
                print(f"❌ Health check failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_manual_update_status(self):
        """Test the manual update status endpoint"""
        print("=" * 60)
        print("TESTING MANUAL UPDATE STATUS")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/manual-update/status")
            print(f"Status endpoint response: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                print("✅ Manual update status endpoint works")
                print(f"   Status: {status_data.get('status')}")
                print(f"   Message: {status_data.get('message')}")
                print("   Features:")
                for feature in status_data.get('features', []):
                    print(f"     - {feature}")
                return True
            else:
                print(f"❌ Status endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Status endpoint error: {e}")
            return False
    
    def test_manual_update_trigger(self, max_articles=100):
        """Test triggering the manual update"""
        print("=" * 60)
        print(f"TESTING MANUAL UPDATE TRIGGER (max_articles={max_articles})")
        print("=" * 60)
        
        try:
            # Test with fixed parameters as specified by user
            payload = {"max_articles": max_articles}
            response = self.session.post(
                f"{self.base_url}/api/manual-update",
                params=payload
            )
            
            print(f"Manual update trigger response: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                print("✅ Manual update triggered successfully")
                print(f"   Success: {result_data.get('success')}")
                print(f"   Message: {result_data.get('message')}")
                print(f"   Max articles: {result_data.get('max_articles')}")
                print("   Process steps:")
                for step in result_data.get('process', []):
                    print(f"     {step}")
                return True
            else:
                print(f"❌ Manual update trigger failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Manual update trigger error: {e}")
            return False
    
    def test_database_connection(self):
        """Test database connection directly"""
        print("=" * 60)
        print("TESTING DATABASE CONNECTION")
        print("=" * 60)
        
        try:
            from scraper.core.database_manager import DatabaseManager
            
            db_manager = DatabaseManager()
            print("✅ DatabaseManager initialized")
            
            # Test connection
            if db_manager.supabase:
                print("✅ Supabase client created")
                
                # Test getting article count
                count = db_manager.get_total_count()
                print(f"✅ Database connection works - {count} articles in database")
                
                # Test environment variables
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_KEY')
                print(f"   SUPABASE_URL: {'set' if supabase_url else 'missing'}")
                print(f"   SUPABASE_KEY: {'set' if supabase_key else 'missing'}")
                
                return True
            else:
                print("❌ Supabase client not created")
                return False
                
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def test_manual_scraper_directly(self):
        """Test the ManualScraper class directly"""
        print("=" * 60)
        print("TESTING MANUAL SCRAPER DIRECTLY")
        print("=" * 60)
        
        try:
            from scraper.core.manual_scraper import ManualScraper
            
            print("✅ ManualScraper imported successfully")
            
            # Initialize scraper
            scraper = ManualScraper()
            print("✅ ManualScraper initialized")
            
            # Check components
            print(f"   Database manager: {'✅' if scraper.db_manager else '❌'}")
            print(f"   Alert logger: {'✅' if scraper.alert_logger else '❌'}")
            print(f"   AI analyzer: {'✅' if scraper.ai_analyzer else '❌'}")
            print(f"   Keywords count: {len(scraper.KEYWORDS)}")
            print(f"   Keywords: {', '.join(scraper.KEYWORDS[:5])}...")
            
            # Test with small number for debugging
            print("\n🧪 Testing with max_articles=5 for debugging...")
            
            def progress_callback(message, log_type):
                print(f"   Progress: {message}")
            
            # Run a small test
            result = scraper.手动更新(max_articles=5, progress_callback=progress_callback)
            
            print("✅ Manual scraper test completed")
            print(f"   Sources processed: {result.get('sources_processed', [])}")
            print(f"   Total articles found: {result.get('total_articles_found', 0)}")
            print(f"   Total articles saved: {result.get('total_articles_saved', 0)}")
            print(f"   Duration: {result.get('duration', 0):.2f} seconds")
            
            if result.get('errors'):
                print("   Errors:")
                for error in result['errors'][:3]:
                    print(f"     - {error}")
            
            return True
            
        except Exception as e:
            print(f"❌ Manual scraper direct test error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_scraper_components(self):
        """Test individual scraper components"""
        print("=" * 60)
        print("TESTING SCRAPER COMPONENTS")
        print("=" * 60)
        
        try:
            # Test BlockBeats scraper
            print("--- Testing BlockBeats Scraper ---")
            from scraper.core.blockbeats_scraper import BlockBeatsScraper
            from scraper.core import Config
            from scraper.core.storage import CSVDataStore
            from datetime import date
            
            # Create test config
            config = Config(
                target_url="https://www.theblockbeats.info/",
                max_articles=5,
                request_delay=1.0,
                timeout=30,
                max_retries=3
            )
            
            # Create temporary data store
            import tempfile
            temp_file = tempfile.mktemp(suffix='.csv')
            data_store = CSVDataStore(temp_file)
            
            # Test date range (last 1 day as specified)
            end_date = date.today()
            start_date = end_date - timedelta(days=1)
            
            # Test keywords (21 security keywords as specified)
            keywords = [
                "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
                "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
                "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
            ]
            
            print(f"   Date range: {start_date} to {end_date}")
            print(f"   Keywords: {len(keywords)} keywords")
            print(f"   Max articles: {config.max_articles}")
            
            # Create scraper
            scraper = BlockBeatsScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=keywords
            )
            
            print("✅ BlockBeats scraper created successfully")
            
            # Test latest ID detection
            latest_id = scraper.find_latest_article_id()
            print(f"   Latest article ID: {latest_id}")
            
            if latest_id:
                print("✅ BlockBeats scraper can find latest articles")
            else:
                print("❌ BlockBeats scraper cannot find latest articles")
            
            # Clean up
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return latest_id is not None
            
        except Exception as e:
            print(f"❌ Scraper components test error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_diagnosis(self):
        """Run complete manual update diagnosis"""
        print("🔍 MANUAL UPDATE API DIAGNOSIS")
        print("=" * 60)
        
        results = {
            'health_check': False,
            'status_endpoint': False,
            'database_connection': False,
            'scraper_components': False,
            'manual_scraper_direct': False,
            'api_trigger': False
        }
        
        # Test 1: Health check
        results['health_check'] = self.test_health_check()
        
        # Test 2: Status endpoint
        results['status_endpoint'] = self.test_manual_update_status()
        
        # Test 3: Database connection
        results['database_connection'] = self.test_database_connection()
        
        # Test 4: Scraper components
        results['scraper_components'] = self.test_scraper_components()
        
        # Test 5: Manual scraper directly (only if components work)
        if results['scraper_components'] and results['database_connection']:
            results['manual_scraper_direct'] = self.test_manual_scraper_directly()
        
        # Test 6: API trigger (only if other tests pass)
        if results['health_check'] and results['status_endpoint']:
            results['api_trigger'] = self.test_manual_update_trigger(max_articles=100)
        
        # Summary
        print("\n" + "=" * 60)
        print("DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Manual update should work correctly.")
        else:
            print("⚠️  Some tests failed. Manual update may have issues.")
            
        return results

def main():
    """Main function to run manual update diagnosis"""
    debugger = ManualUpdateDebugger()
    
    # Check if we should test against local or remote server
    import sys
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        debugger.base_url = base_url
        print(f"Testing against: {base_url}")
    else:
        print("Testing against: http://localhost:8000")
        print("To test against remote server, run: python debug_manual_update_api.py https://crypto-news-scraper.onrender.com")
    
    try:
        debugger.run_full_diagnosis()
    except KeyboardInterrupt:
        print("\n🛑 Diagnosis interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnosis failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()