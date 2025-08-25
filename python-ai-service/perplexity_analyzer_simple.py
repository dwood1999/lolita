#!/usr/bin/env python3
"""
Simple Perplexity Market Research Integration
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import httpx
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerplexityResult:
    """Perplexity market research result"""
    
    market_trends: Optional[Dict[str, Any]] = None
    competitive_landscape: Optional[Dict[str, Any]] = None
    recent_industry_data: Optional[Dict[str, Any]] = None
    platform_strategies: Optional[Dict[str, Any]] = None
    star_power_analysis: Optional[Dict[str, Any]] = None
    budget_benchmarks: Optional[Dict[str, Any]] = None
    sources_cited: List[str] = None
    
    market_opportunity_score: float = 0.0
    competitive_advantage: str = ""
    market_recommendation: str = ""
    
    processing_time: float = 0.0
    cost: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    research_date: str = ""
    data_freshness: str = ""

class PerplexityAnalyzer:
    """Simple Perplexity AI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar"
        
        if not self.api_key:
            logger.warning("⚠️  PERPLEXITY_API_KEY not set - Perplexity market research will be disabled")
        else:
            logger.info("📊 Perplexity Market Research Analyzer initialized")
    
    async def research_market_intelligence(
        self, 
        title: str, 
        genre: str,
        release_timeframe: str = "next_12_months",
        budget_range: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> Optional[PerplexityResult]:
        """Market research analysis"""
        
        if not self.api_key:
            logger.warning("❌ Perplexity market research skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Simple prompt for testing
            prompt = f"Research market trends for {genre} films like '{title}'. Provide brief analysis of current market opportunities."

            response = await self._call_perplexity_api(prompt)
            
            processing_time = time.time() - start_time
            
            # Calculate a simple dynamic score based on response content
            dynamic_score = self._calculate_simple_market_score(response, genre, title)
            
            result = PerplexityResult(
                market_trends={"content": response},
                market_opportunity_score=dynamic_score,
                competitive_advantage="Market analysis completed",
                market_recommendation=self._get_simple_recommendation(dynamic_score),
                research_date=datetime.now().isoformat(),
                data_freshness="Current",
                processing_time=processing_time,
                cost=0.01,
                success=True,
                error_message=None
            )
            
            logger.info(f"📊 Perplexity market research complete in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Perplexity market research failed: {e}")
            return PerplexityResult(
                market_opportunity_score=0.0,
                competitive_advantage="Analysis failed",
                market_recommendation="Research unavailable",
                research_date=datetime.now().isoformat(),
                data_freshness="Failed",
                processing_time=0,
                cost=0,
                success=False,
                error_message=str(e)
            )
    
    async def _call_perplexity_api(self, prompt: str) -> str:
        """Call Perplexity API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_completion_tokens": 500
        }
        
        timeout = httpx.Timeout(connect=30.0, read=60.0, write=30.0, pool=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception("No response content from Perplexity")
            else:
                error_text = response.text
                raise Exception(f"Perplexity API error {response.status_code}: {error_text}")
    
    def to_database_format(self, result: PerplexityResult) -> Dict[str, Any]:
        """Convert to database format"""
        return {
            'perplexity_market_trends': json.dumps(result.market_trends) if result.market_trends else None,
            'perplexity_competitive_analysis': json.dumps(result.competitive_landscape) if result.competitive_landscape else None,
            'perplexity_industry_reports': json.dumps(result.recent_industry_data) if result.recent_industry_data else None,
            'perplexity_distribution_strategy': json.dumps(result.platform_strategies) if result.platform_strategies else None,
            'perplexity_talent_intelligence': json.dumps(result.star_power_analysis) if result.star_power_analysis else None,
            'perplexity_financial_intelligence': json.dumps(result.budget_benchmarks) if result.budget_benchmarks else None,
            'perplexity_sources_cited': json.dumps(result.sources_cited) if result.sources_cited else None,
            'perplexity_market_score': float(result.market_opportunity_score) if result.market_opportunity_score is not None else None,
            'perplexity_competitive_advantage': str(result.competitive_advantage) if result.competitive_advantage else None,
            'perplexity_recommendation': str(result.market_recommendation) if result.market_recommendation else None,
            'perplexity_cost': float(result.cost) if result.cost is not None else None,
            'perplexity_processing_time': float(result.processing_time) if result.processing_time is not None else None,
            'perplexity_research_date': result.research_date if result.research_date else None,
            'perplexity_data_freshness': str(result.data_freshness) if result.data_freshness else None,
            'perplexity_success': bool(result.success) if result.success is not None else None,
            'perplexity_error_message': str(result.error_message) if result.error_message else None
        }
    
    def _calculate_simple_market_score(self, response: str, genre: str, title: str) -> float:
        """Calculate simple dynamic market score based on response content"""
        
        base_score = 6.0  # Start slightly above middle for simple analyzer
        response_lower = response.lower()
        
        # Simple positive market indicators
        positive_indicators = [
            'strong market', 'growing demand', 'popular genre', 'successful',
            'profitable', 'high potential', 'favorable', 'trending',
            'audience interest', 'commercial appeal', 'box office'
        ]
        
        # Simple negative market indicators
        negative_indicators = [
            'declining market', 'oversaturated', 'limited appeal', 'risky',
            'challenging', 'difficult', 'poor performance', 'weak demand',
            'niche audience', 'limited commercial'
        ]
        
        # Count indicators
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        # Adjust score based on indicators
        base_score += (positive_count * 0.3) - (negative_count * 0.4)
        
        # Simple genre adjustments
        if genre.lower() in ['action', 'comedy', 'horror']:
            base_score += 0.3  # Generally more commercial
        elif genre.lower() in ['drama', 'documentary']:
            base_score -= 0.2  # Generally less commercial
        
        # Add simple randomness for variation
        import hashlib
        content_hash = int(hashlib.md5(f"{title}{genre}{response}".encode()).hexdigest()[:8], 16)
        import random
        random.seed(content_hash % 2147483647)
        variation = (random.random() - 0.5) * 0.6  # ±0.3 variation
        base_score += variation
        
        # Ensure bounds
        final_score = max(1.0, min(10.0, base_score))
        
        logger.info(f"📊 Simple Perplexity score: Positive={positive_count}, "
                   f"Negative={negative_count}, Genre={genre} → Score={final_score:.1f}/10")
        
        return final_score
    
    def _get_simple_recommendation(self, score: float) -> str:
        """Get simple recommendation based on calculated score"""
        if score >= 8.0:
            return "Strong market opportunity - proceed with confidence"
        elif score >= 6.5:
            return "Favorable market conditions - good potential"
        elif score >= 5.0:
            return "Moderate opportunity - careful positioning required"
        elif score >= 3.0:
            return "Challenging market - consider risks"
        else:
            return "Limited market opportunity - high risk"
