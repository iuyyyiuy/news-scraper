#!/usr/bin/env python3
"""
Debug Jinse latest article ID detection
"""
import requests
import re
from datetime import datetime

def test_jinse_latest_id():
    """Test finding the latest Jinse article ID"""
    print("🔍 Testing Jinse Latest Article ID Detection")
    print("=" * 60)
    
    try:
        # Test the main lives page
        print("1️⃣ Testing main lives page...")
        response = requests.get("https://www.jinse.com.cn/lives", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Look for article links
            pattern = r'/lives/(\d+)\.html'
            matches = re.findall(pattern, response.text)
            
            print(f"Found {len(matches)} article ID matches")
            
            if matches:
                # Show first few matches
                print("First 10 matches:")
                for i, match in enumerate(matches[:10]):
                    print(f"  {i+1}. ID: {match}")
                
                # Get the highest ID
                latest_id = max(int(id_str) for id_str in matches)
                print(f"\n🎯 Latest ID found: {latest_id}")
                
                # Test accessing this article
                test_url = f"https://www.jinse.com.cn/lives/{latest_id}.html"
                print(f"\n2️⃣ Testing latest article access...")
                print(f"URL: {test_url}")
                
                test_response = requests.get(test_url, timeout=10)
                print(f"Status: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    # Try to extract title
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(test_response.text, 'html.parser')
                    
                    title_elem = soup.select_one('span.title')
                    title = title_elem.get_text(strip=True) if title_elem else "No title found"
                    
                    print(f"Title: {title[:100]}...")
                    
                    # Check for content
                    content_elem = soup.select_one('p.content')
                    content = content_elem.get_text(strip=True) if content_elem else "No content found"
                    
                    print(f"Content: {content[:100]}...")
                    
                    return latest_id
                else:
                    print(f"❌ Cannot access latest article: {test_response.status_code}")
            else:
                print("❌ No article IDs found in page")
                
                # Debug: show part of the page content
                print("\n🔍 Page content sample (first 1000 chars):")
                print(response.text[:1000])
                print("...")
        else:
            print(f"❌ Cannot access main page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_alternative_methods():
    """Test alternative methods to find latest ID"""
    print("\n3️⃣ Testing alternative methods...")
    
    # Method 1: Try the API endpoint if it exists
    try:
        print("Testing API endpoint...")
        api_response = requests.get("https://www.jinse.com.cn/api/lives", timeout=10)
        print(f"API Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            print("API response sample:")
            print(api_response.text[:500])
    except:
        print("API endpoint not available")
    
    # Method 2: Try different page patterns
    try:
        print("\nTesting different page patterns...")
        
        # Try the news flash page
        flash_response = requests.get("https://www.jinse.com.cn/newsflash", timeout=10)
        print(f"Newsflash Status: {flash_response.status_code}")
        
        if flash_response.status_code == 200:
            pattern = r'/lives/(\d+)\.html'
            matches = re.findall(pattern, flash_response.text)
            if matches:
                latest_from_flash = max(int(id_str) for id_str in matches)
                print(f"Latest ID from newsflash: {latest_from_flash}")
            else:
                print("No IDs found in newsflash page")
                
    except Exception as e:
        print(f"Alternative methods failed: {e}")

def test_current_working_articles():
    """Test some known working article IDs"""
    print("\n4️⃣ Testing known working article ranges...")
    
    # Test a range around a reasonable current ID
    test_ids = [493415, 493414, 493413, 493410, 493400]  # Based on what we saw earlier
    
    for test_id in test_ids:
        try:
            url = f"https://www.jinse.com.cn/lives/{test_id}.html"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                title_elem = soup.select_one('span.title')
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                
                print(f"✅ ID {test_id}: {title[:50]}...")
            else:
                print(f"❌ ID {test_id}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ ID {test_id}: Error {e}")

if __name__ == "__main__":
    latest_id = test_jinse_latest_id()
    test_alternative_methods()
    test_current_working_articles()
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSIS:")
    if latest_id:
        print(f"✅ Latest ID detection working: {latest_id}")
    else:
        print("❌ Latest ID detection failed")
        print("💡 Possible issues:")
        print("   - Page structure changed")
        print("   - Different URL pattern")
        print("   - Anti-scraping measures")
        print("   - Network/timeout issues")
    print("=" * 60)