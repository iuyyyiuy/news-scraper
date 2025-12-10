"""
AI Content Analyzer using DeepSeek API
Provides intelligent keyword matching and duplicate detection
"""

import os
import json
import hashlib
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from .alert_logger import AlertLogger

# Load environment variables
load_dotenv()

class AIContentAnalyzer:
    """
    AI-powered content analysis using DeepSeek API for:
    1. Intelligent keyword relevance scoring
    2. Duplicate content detection
    3. Content quality assessment
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Content Analyzer
        
        Args:
            api_key: DeepSeek API key (if not provided, will look for DEEPSEEK_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass api_key parameter.")
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.alert_logger = AlertLogger()
        
        # Keywords for security-related news
        self.security_keywords = [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ]
    
    def analyze_content_relevance(self, title: str, content: str, keywords: List[str]) -> Dict[str, any]:
        """
        Analyze if content is truly relevant to the matched keywords using AI.
        
        Args:
            title: Article title
            content: Article content
            keywords: List of matched keywords
            
        Returns:
            Dictionary with relevance analysis results
        """
        try:
            # Create prompt for AI analysis
            prompt = self._create_relevance_prompt(title, content, keywords)
            
            # Call DeepSeek API
            response = self._call_deepseek_api(prompt)
            
            if response:
                # Parse AI response
                analysis = self._parse_relevance_response(response)
                
                self.alert_logger.log_info(
                    component="AIContentAnalyzer",
                    message=f"Content relevance analyzed for keywords: {keywords}",
                    details={
                        "title": title[:100],
                        "keywords": keywords,
                        "relevance_score": analysis.get('relevance_score', 0),
                        "is_relevant": analysis.get('is_relevant', False)
                    }
                )
                
                return analysis
            else:
                # Fallback to simple keyword matching
                return self._fallback_relevance_analysis(title, content, keywords)
                
        except Exception as e:
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message="Error in AI content relevance analysis",
                details={"title": title[:100], "keywords": keywords},
                exception=e
            )
            # Fallback to simple analysis
            return self._fallback_relevance_analysis(title, content, keywords)
    
    def detect_duplicate_content(self, new_article: Dict[str, str], existing_articles: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Detect if new article is a duplicate of existing articles using AI.
        
        Args:
            new_article: New article with 'title' and 'content' keys
            existing_articles: List of existing articles to compare against
            
        Returns:
            Dictionary with duplicate detection results
        """
        try:
            # First, do quick hash-based check
            new_hash = self._calculate_content_hash(new_article['content'])
            
            for existing in existing_articles:
                existing_hash = self._calculate_content_hash(existing['content'])
                if new_hash == existing_hash:
                    return {
                        'is_duplicate': True,
                        'duplicate_type': 'exact_match',
                        'similarity_score': 100.0,
                        'duplicate_article': existing,
                        'reason': 'Identical content hash'
                    }
            
            # If no exact match, use AI for semantic similarity
            if len(existing_articles) > 0:
                # Compare with most recent articles (limit to 5 for API efficiency)
                recent_articles = existing_articles[:5]
                
                prompt = self._create_duplicate_prompt(new_article, recent_articles)
                response = self._call_deepseek_api(prompt)
                
                if response:
                    analysis = self._parse_duplicate_response(response)
                    
                    self.alert_logger.log_info(
                        component="AIContentAnalyzer",
                        message="Duplicate detection completed",
                        details={
                            "new_title": new_article['title'][:100],
                            "compared_articles": len(recent_articles),
                            "is_duplicate": analysis.get('is_duplicate', False),
                            "similarity_score": analysis.get('similarity_score', 0)
                        }
                    )
                    
                    return analysis
            
            # No duplicates found
            return {
                'is_duplicate': False,
                'duplicate_type': None,
                'similarity_score': 0.0,
                'duplicate_article': None,
                'reason': 'No similar content found'
            }
            
        except Exception as e:
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message="Error in AI duplicate detection",
                details={"new_title": new_article['title'][:100]},
                exception=e
            )
            # Fallback to simple hash comparison
            return self._fallback_duplicate_detection(new_article, existing_articles)
    
    def _create_relevance_prompt(self, title: str, content: str, keywords: List[str]) -> str:
        """Create prompt for relevance analysis."""
        return f"""
Analyze if this cryptocurrency/blockchain news article is truly relevant to the given security-related keywords.

Article Title: {title}

Article Content: {content[:1000]}...

Matched Keywords: {', '.join(keywords)}

Please analyze:
1. Is this article genuinely related to the matched keywords in a meaningful way?
2. Rate the relevance on a scale of 0-100 (0 = not relevant, 100 = highly relevant)
3. Provide a brief explanation of why it is or isn't relevant

Consider that we're looking for news about:
- Security incidents (hacks, breaches, vulnerabilities)
- Regulatory compliance and enforcement
- Financial crimes (money laundering, fraud)
- Exchange issues (bankruptcies, delistings)
- Risk management and security measures

Respond in JSON format:
{{
    "is_relevant": true/false,
    "relevance_score": 0-100,
    "explanation": "brief explanation",
    "matched_concepts": ["list of actual security concepts found"]
}}
"""
    
    def _create_duplicate_prompt(self, new_article: Dict[str, str], existing_articles: List[Dict[str, str]]) -> str:
        """Create prompt for duplicate detection."""
        existing_summaries = []
        for i, article in enumerate(existing_articles):
            existing_summaries.append(f"Article {i+1}: {article['title']}\nContent: {article['content'][:300]}...")
        
        return f"""
Analyze if this new cryptocurrency news article is a duplicate or very similar to any of the existing articles.

NEW ARTICLE:
Title: {new_article['title']}
Content: {new_article['content'][:500]}...

EXISTING ARTICLES:
{chr(10).join(existing_summaries)}

Please determine:
1. Is the new article a duplicate or substantially similar (>90% same content) to any existing article?
2. What is the similarity score (0-100) with the most similar existing article?
3. Which existing article is most similar (if any)?

Consider articles as duplicates if they:
- Report the same event/news
- Have very similar content (>90% overlap)
- Are just minor rewrites of the same story

Respond in JSON format:
{{
    "is_duplicate": true/false,
    "similarity_score": 0-100,
    "most_similar_index": 0-4 or null,
    "explanation": "brief explanation"
}}
"""
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """Call DeepSeek API with the given prompt."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent analysis
                "max_tokens": 500
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.alert_logger.log_error(
                    component="AIContentAnalyzer",
                    message=f"DeepSeek API error: {response.status_code}",
                    details={"response": response.text}
                )
                return None
                
        except Exception as e:
            self.alert_logger.log_error(
                component="AIContentAnalyzer",
                message="Error calling DeepSeek API",
                exception=e
            )
            return None
    
    def _parse_relevance_response(self, response: str) -> Dict[str, any]:
        """Parse AI response for relevance analysis."""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                
                result = json.loads(json_str)
                
                return {
                    'is_relevant': result.get('is_relevant', False),
                    'relevance_score': result.get('relevance_score', 0),
                    'explanation': result.get('explanation', ''),
                    'matched_concepts': result.get('matched_concepts', [])
                }
            else:
                # Fallback parsing
                is_relevant = 'true' in response.lower() or 'relevant' in response.lower()
                return {
                    'is_relevant': is_relevant,
                    'relevance_score': 50 if is_relevant else 10,
                    'explanation': response[:200],
                    'matched_concepts': []
                }
                
        except Exception as e:
            self.alert_logger.log_warning(
                component="AIContentAnalyzer",
                message="Error parsing AI relevance response",
                details={"response": response[:200]},
                exception=e
            )
            return {
                'is_relevant': False,
                'relevance_score': 0,
                'explanation': 'Failed to parse AI response',
                'matched_concepts': []
            }
    
    def _parse_duplicate_response(self, response: str) -> Dict[str, any]:
        """Parse AI response for duplicate detection."""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                
                result = json.loads(json_str)
                
                return {
                    'is_duplicate': result.get('is_duplicate', False),
                    'similarity_score': result.get('similarity_score', 0),
                    'most_similar_index': result.get('most_similar_index'),
                    'explanation': result.get('explanation', ''),
                    'duplicate_type': 'ai_detected' if result.get('is_duplicate') else None
                }
            else:
                # Fallback parsing
                is_duplicate = 'true' in response.lower() or 'duplicate' in response.lower()
                return {
                    'is_duplicate': is_duplicate,
                    'similarity_score': 90 if is_duplicate else 10,
                    'explanation': response[:200],
                    'duplicate_type': 'ai_detected' if is_duplicate else None
                }
                
        except Exception as e:
            self.alert_logger.log_warning(
                component="AIContentAnalyzer",
                message="Error parsing AI duplicate response",
                details={"response": response[:200]},
                exception=e
            )
            return {
                'is_duplicate': False,
                'similarity_score': 0,
                'explanation': 'Failed to parse AI response',
                'duplicate_type': None
            }
    
    def _fallback_relevance_analysis(self, title: str, content: str, keywords: List[str]) -> Dict[str, any]:
        """Fallback relevance analysis using simple keyword matching."""
        text = (title + ' ' + content).lower()
        
        # Count keyword occurrences
        keyword_count = 0
        matched_concepts = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                keyword_count += text.count(keyword.lower())
                matched_concepts.append(keyword)
        
        # Simple scoring based on keyword frequency
        relevance_score = min(keyword_count * 20, 100)  # Cap at 100
        is_relevant = relevance_score >= 40  # Threshold for relevance
        
        return {
            'is_relevant': is_relevant,
            'relevance_score': relevance_score,
            'explanation': f'Simple keyword matching: {keyword_count} occurrences',
            'matched_concepts': matched_concepts
        }
    
    def _fallback_duplicate_detection(self, new_article: Dict[str, str], existing_articles: List[Dict[str, str]]) -> Dict[str, any]:
        """Fallback duplicate detection using content hashing."""
        new_hash = self._calculate_content_hash(new_article['content'])
        
        for existing in existing_articles:
            existing_hash = self._calculate_content_hash(existing['content'])
            if new_hash == existing_hash:
                return {
                    'is_duplicate': True,
                    'duplicate_type': 'hash_match',
                    'similarity_score': 100.0,
                    'duplicate_article': existing,
                    'explanation': 'Identical content hash'
                }
        
        return {
            'is_duplicate': False,
            'duplicate_type': None,
            'similarity_score': 0.0,
            'duplicate_article': None,
            'explanation': 'No hash matches found'
        }
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for duplicate detection."""
        # Normalize content: remove whitespace, convert to lowercase
        normalized = ''.join(content.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def analyze_article_batch(self, articles: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Analyze a batch of articles for relevance and duplicates.
        
        Args:
            articles: List of articles with title, content, and matched_keywords
            
        Returns:
            List of articles with AI analysis results
        """
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            try:
                # Analyze relevance
                relevance = self.analyze_content_relevance(
                    article['title'],
                    article['content'],
                    article.get('matched_keywords', [])
                )
                
                # Analyze duplicates against previously processed articles
                duplicate_check = self.detect_duplicate_content(
                    {'title': article['title'], 'content': article['content']},
                    analyzed_articles
                )
                
                # Add analysis results to article
                article['ai_analysis'] = {
                    'relevance': relevance,
                    'duplicate_check': duplicate_check,
                    'analyzed_at': datetime.now().isoformat()
                }
                
                # Only add to analyzed list if not a duplicate
                if not duplicate_check['is_duplicate']:
                    analyzed_articles.append(article)
                else:
                    self.alert_logger.log_info(
                        component="AIContentAnalyzer",
                        message="Duplicate article detected and filtered",
                        details={
                            "title": article['title'][:100],
                            "similarity_score": duplicate_check['similarity_score']
                        }
                    )
                
            except Exception as e:
                self.alert_logger.log_error(
                    component="AIContentAnalyzer",
                    message=f"Error analyzing article {i}",
                    details={"title": article.get('title', 'Unknown')[:100]},
                    exception=e
                )
                # Keep article without analysis
                analyzed_articles.append(article)
        
        return analyzed_articles