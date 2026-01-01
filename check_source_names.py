#!/usr/bin/env python3
"""
Check and analyze source name inconsistencies in the database.
"""

from scraper.core.database_manager import DatabaseManager

def check_source_names():
    """Check what source names currently exist in the database."""
    
    db_manager = DatabaseManager()
    
    try:
        # Get all unique source names
        response = db_manager.supabase.table('articles').select('source').execute()
        
        if not response.data:
            print("❌ No articles found in database")
            return
        
        # Count occurrences of each source name
        source_counts = {}
        for article in response.data:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("=== CURRENT SOURCE NAMES IN DATABASE ===")
        print(f"Total articles: {len(response.data)}")
        print("\nSource name distribution:")
        
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  '{source}': {count} articles")
        
        # Identify what needs to be normalized
        print("\n=== NORMALIZATION NEEDED ===")
        
        blockbeats_variants = []
        jinse_variants = []
        other_sources = []
        
        for source in source_counts.keys():
            source_lower = source.lower()
            if 'blockbeat' in source_lower or 'theblockbeats' in source_lower:
                if source != 'BlockBeats':
                    blockbeats_variants.append(source)
            elif 'jinse' in source_lower:
                if source != 'Jinse':
                    jinse_variants.append(source)
            else:
                other_sources.append(source)
        
        if blockbeats_variants:
            print(f"\nBlockBeats variants to normalize: {blockbeats_variants}")
            total_blockbeats = sum(source_counts[variant] for variant in blockbeats_variants)
            print(f"  Total articles to update: {total_blockbeats}")
        
        if jinse_variants:
            print(f"\nJinse variants to normalize: {jinse_variants}")
            total_jinse = sum(source_counts[variant] for variant in jinse_variants)
            print(f"  Total articles to update: {total_jinse}")
        
        if other_sources:
            print(f"\nOther sources found: {other_sources}")
        
        # Check if normalization is needed
        needs_normalization = len(blockbeats_variants) > 0 or len(jinse_variants) > 0
        
        if needs_normalization:
            print(f"\n⚠️  Database needs source name normalization")
            return True
        else:
            print(f"\n✅ All source names are already standardized")
            return False
            
    except Exception as e:
        print(f"❌ Error checking source names: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_source_names()