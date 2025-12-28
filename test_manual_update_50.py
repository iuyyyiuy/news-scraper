#!/usr/bin/env python3
"""
Test manual update with 50 articles per source
"""
from scraper.core.manual_scraper import ManualScraper
from datetime import datetime

def progress_callback(message, status):
    print(f'[{status.upper()}] {message}')

def main():
    print('🧪 Testing manual update with 50 articles per source...')
    print('=' * 60)
    
    try:
        scraper = ManualScraper()
        
        # Test with 50 articles per source
        print('📋 Starting 手动更新 with 50 articles per source...')
        print('🔍 This will search more articles to find security-related news')
        print()
        
        result = scraper.手动更新(
            max_articles=50,
            progress_callback=progress_callback
        )
        
        print()
        print('=' * 60)
        print('📊 手动更新 Results (50 articles per source):')
        print('=' * 60)
        print(f'⏱️  Duration: {result["duration"]:.2f} seconds')
        print(f'📰 Total articles found: {result["total_articles_found"]}')
        print(f'💾 Total articles saved: {result["total_articles_saved"]}')
        print(f'🔄 Total duplicates skipped: {result["total_duplicates_skipped"]}')
        print(f'🤖 AI filtered articles: {result["ai_filtered_count"]}')
        print(f'📝 Sources processed: {result["sources_processed"]}')
        
        if result['errors']:
            print(f'⚠️  Errors encountered: {len(result["errors"])}')
            for error in result['errors'][:3]:  # Show first 3 errors
                print(f'   - {error}')
        else:
            print('✅ No errors encountered')
        
        print()
        print('📋 Source breakdown:')
        for source in result['sources_processed']:
            if source in result['source_results']:
                src_result = result['source_results'][source]
                print(f'   {source.upper()}:')
                print(f'     Found: {src_result["articles_found"]} articles')
                print(f'     Saved: {src_result["articles_saved"]} articles')
                print(f'     Duplicates: {src_result["duplicates_skipped"]} articles')
                print(f'     AI filtered: {src_result.get("ai_filtered", 0)} articles')
                print(f'     Duration: {src_result["duration"]:.2f}s')
        
        if result['total_articles_saved'] > 0:
            print()
            print('🎉 Success! Found and saved new articles!')
            print('💡 The manual update is working - it found security-related news')
        else:
            print()
            print('ℹ️  No new articles saved. This could mean:')
            print('   1. No articles matched the 21 security keywords')
            print('   2. All found articles were duplicates of existing ones')
            print('   3. AI filtered out articles as not relevant enough')
            print('   4. Network issues prevented scraping some sources')
            
        return True
        
    except Exception as e:
        print(f'❌ 手动更新 test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()