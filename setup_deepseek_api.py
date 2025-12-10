#!/usr/bin/env python3
"""
Setup script for DeepSeek API integration.
"""

import os

def setup_deepseek_api():
    """Setup DeepSeek API key for AI content analysis."""
    
    print("=== DEEPSEEK API SETUP ===")
    print()
    print("To enable AI-powered content analysis, you need to set up your DeepSeek API key.")
    print()
    print("1. Get your API key from: https://platform.deepseek.com/")
    print("2. Add it to your environment variables")
    print()
    
    # Check if already configured
    existing_key = os.getenv('DEEPSEEK_API_KEY')
    if existing_key:
        print(f"✅ DeepSeek API key is already configured (ends with: ...{existing_key[-8:]})")
        
        # Test the API
        try:
            from scraper.core.ai_content_analyzer import AIContentAnalyzer
            analyzer = AIContentAnalyzer()
            print("✅ AI Content Analyzer can be initialized successfully")
            
            # Quick test
            print("\n🧪 Running quick API test...")
            test_result = analyzer.analyze_content_relevance(
                "Test article about Bitcoin price",
                "Bitcoin price increased today due to market conditions.",
                ["监管"]
            )
            
            if test_result.get('relevance_score') is not None:
                print("✅ DeepSeek API is working correctly!")
                print(f"   Test relevance score: {test_result['relevance_score']}/100")
            else:
                print("⚠️ API test returned unexpected result")
                
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            print("Please check your API key and try again.")
        
        return
    
    print("❌ DeepSeek API key not found in environment variables")
    print()
    print("To set up the API key:")
    print()
    print("Option 1: Add to .env file")
    print("echo 'DEEPSEEK_API_KEY=your-api-key-here' >> .env")
    print()
    print("Option 2: Export environment variable")
    print("export DEEPSEEK_API_KEY='your-api-key-here'")
    print()
    print("Option 3: Add to your shell profile (~/.bashrc or ~/.zshrc)")
    print("echo 'export DEEPSEEK_API_KEY=\"your-api-key-here\"' >> ~/.zshrc")
    print()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("📝 Found .env file. You can add your API key there:")
        print("DEEPSEEK_API_KEY=your-api-key-here")
    else:
        print("📝 No .env file found. Creating one...")
        with open('.env', 'a') as f:
            f.write('\n# DeepSeek API Configuration\n')
            f.write('# DEEPSEEK_API_KEY=your-api-key-here\n')
        print("✅ Created .env file with placeholder for API key")
    
    print()
    print("🔧 Benefits of AI Content Analysis:")
    print("   • More accurate keyword relevance detection")
    print("   • Intelligent duplicate content filtering")
    print("   • Improved content quality assessment")
    print("   • Reduced false positives in news filtering")
    print()
    print("After setting up the API key, run: python test_ai_analyzer.py")

if __name__ == "__main__":
    setup_deepseek_api()