#!/usr/bin/env python3
"""
Normalize source names in the database to standardized format.
"""

from scraper.core.database_manager import DatabaseManager

def normalize_source_names():
    """Normalize all source names to standard format: BlockBeats and Jinse."""
    
    db_manager = DatabaseManager()
    
    try:
        print("=== NORMALIZING SOURCE NAMES ===")
        
        # Define normalization mappings
        normalization_map = {
            'blockbeat': 'BlockBeats',
            'theblockbeats.info': 'BlockBeats',
            'theblockbeats': 'BlockBeats',
            'jinse': 'Jinse',
            'jinse.cn': 'Jinse',
            'jinse.com': 'Jinse'
        }
        
        total_updated = 0
        
        for old_name, new_name in normalization_map.items():
            print(f"\n🔄 Updating '{old_name}' → '{new_name}'")
            
            try:
                # Update articles with this source name
                response = db_manager.supabase.table('articles').update({
                    'source': new_name
                }).eq('source', old_name).execute()
                
                # Count how many were updated
                if hasattr(response, 'data') and response.data:
                    updated_count = len(response.data)
                else:
                    # If no data returned, check by querying
                    check_response = db_manager.supabase.table('articles').select('id').eq('source', old_name).execute()
                    updated_count = len(check_response.data) if check_response.data else 0
                
                if updated_count > 0:
                    print(f"   ✅ Updated {updated_count} articles")
                    total_updated += updated_count
                else:
                    print(f"   ℹ️  No articles found with source '{old_name}'")
                    
            except Exception as e:
                print(f"   ❌ Error updating '{old_name}': {e}")
        
        print(f"\n📊 NORMALIZATION COMPLETE")
        print(f"Total articles updated: {total_updated}")
        
        # Verify the results
        print(f"\n🔍 Verifying results...")
        response = db_manager.supabase.table('articles').select('source').execute()
        
        if response.data:
            source_counts = {}
            for article in response.data:
                source = article.get('source', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"Current source distribution:")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  '{source}': {count} articles")
            
            # Check if normalization was successful
            expected_sources = {'BlockBeats', 'Jinse'}
            actual_sources = set(source_counts.keys())
            
            if actual_sources.issubset(expected_sources):
                print(f"\n✅ SUCCESS: All source names are now standardized!")
                return True
            else:
                unexpected = actual_sources - expected_sources
                print(f"\n⚠️  WARNING: Still have non-standard sources: {unexpected}")
                return False
        else:
            print(f"❌ No articles found after normalization")
            return False
            
    except Exception as e:
        print(f"❌ Error during normalization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    normalize_source_names()