#!/usr/bin/env python3
"""
Fix AI Analyzer - Make it less aggressive in filtering articles
The current AI analyzer is filtering out too many relevant articles
"""

import os
import sys
from pathlib import Path

def fix_ai_analyzer():
    """Make AI analyzer less aggressive by adjusting thresholds"""
    
    ai_analyzer_path = Path("scraper/core/ai_content_analyzer.py")
    
    if not ai_analyzer_path.exists():
        print("❌ AI analyzer file not found")
        return False
    
    # Read current content
    with open(ai_analyzer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make the AI analyzer less strict
    # 1. Lower the relevance threshold
    # 2. Add fallback for borderline cases
    # 3. Be more permissive with financial/regulatory content
    
    # Find the relevance prompt and make it less strict
    old_prompt = '''Consider that we're looking for news about:
- Security incidents (hacks, breaches, vulnerabilities)
- Regulatory compliance and enforcement
- Financial crimes (money laundering, fraud)
- Exchange issues (bankruptcies, delistings)
- Risk management and security measures'''
    
    new_prompt = '''Consider that we're looking for news about:
- Security incidents (hacks, breaches, vulnerabilities)
- Regulatory compliance and enforcement
- Financial crimes (money laundering, fraud)
- Exchange issues (bankruptcies, delistings, financial disputes)
- Risk management and security measures
- Corporate governance issues and transparency problems
- Leadership disputes that may affect platform security
- Financial irregularities or accounting issues

Be more inclusive - if there's any reasonable connection to financial security, 
regulatory issues, or platform stability, consider it relevant.'''
    
    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        print("✅ Updated relevance criteria to be more inclusive")
    
    # Also add a fallback mechanism for borderline cases
    fallback_method = '''
    def _fallback_relevance_analysis(self, title: str, content: str, keywords: List[str]) -> Dict[str, any]:
        """
        Fallback relevance analysis when AI is unavailable or fails.
        More permissive than AI analysis.
        """
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Check for any keyword matches (case insensitive)
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in title_lower or keyword.lower() in content_lower:
                matched_keywords.append(keyword)
        
        # Additional financial/regulatory terms that should be considered relevant
        financial_terms = [
            '财务', '透明', '监管', '合规', '风险', '安全', '破产', 
            '下架', '停牌', '暂停', '调查', '执法', '违规', '处罚'
        ]
        
        financial_matches = []
        for term in financial_terms:
            if term in title_lower or term in content_lower:
                financial_matches.append(term)
        
        # Be more permissive - if we have any matches, consider it relevant
        has_matches = len(matched_keywords) > 0 or len(financial_matches) > 0
        
        # Calculate relevance score
        if len(matched_keywords) > 0:
            relevance_score = min(80, 40 + len(matched_keywords) * 20)  # Higher base score
        elif len(financial_matches) > 0:
            relevance_score = min(70, 30 + len(financial_matches) * 15)  # Financial terms get good score
        else:
            relevance_score = 10
        
        return {
            'is_relevant': has_matches,
            'relevance_score': relevance_score,
            'explanation': f'Matched keywords: {matched_keywords}, Financial terms: {financial_matches}',
            'matched_concepts': matched_keywords + financial_matches
        }'''
    
    # Find where to insert the fallback method
    if 'def _fallback_relevance_analysis(' not in content:
        # Insert before the _create_relevance_prompt method
        insert_point = content.find('def _create_relevance_prompt(')
        if insert_point > 0:
            content = content[:insert_point] + fallback_method + '\n    ' + content[insert_point:]
            print("✅ Added more permissive fallback analysis method")
    
    # Write the updated content
    with open(ai_analyzer_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ AI analyzer has been made less aggressive")
    print("📊 Changes made:")
    print("   - More inclusive relevance criteria")
    print("   - Added financial/regulatory terms recognition")
    print("   - Higher base relevance scores")
    print("   - More permissive fallback analysis")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing AI Analyzer - Making it less aggressive...")
    print("=" * 60)
    
    if fix_ai_analyzer():
        print("\n🎉 AI analyzer fix completed!")
        print("\n📋 Next steps:")
        print("1. Test the updated analyzer")
        print("2. Run a manual scrape to verify it's working")
        print("3. Deploy the fix to production")
    else:
        print("\n❌ Fix failed!")
        sys.exit(1)