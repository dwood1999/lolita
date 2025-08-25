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
            
            # Comprehensive market research prompt
            prompt = f"""Analyze the current market opportunity for a {genre} film titled '{title}'. 

Provide detailed analysis covering:

1. **Current Market Trends**: What are the current trends in {genre} films? What's performing well at the box office?

2. **Competitive Landscape**: What similar films have been released recently? How did they perform commercially?

3. **Target Demographics**: Who is the primary audience for {genre} films? What are their viewing habits and preferences?

4. **Market Timing**: Is this a good time to release a {genre} film? Are there seasonal considerations?

5. **Distribution Strategy**: What's the optimal release strategy for {genre} films in the current market?

6. **Commercial Viability**: Based on recent market data, what's the commercial potential for this type of film?

Please provide specific examples, box office data where available, and actionable insights for producers and distributors."""

            response = await self._call_perplexity_api(prompt)
            
            processing_time = time.time() - start_time
            
            # Calculate dynamic market score based on response content
            market_score = self._calculate_market_score(response, genre, title)
            competitive_advantage = self._extract_competitive_advantage(response)
            recommendation = self._generate_market_recommendation(market_score, response)
            
            result = PerplexityResult(
                market_trends={"content": response},
                competitive_landscape={"content": self._extract_competitive_analysis(response)},
                recent_industry_data={"content": self._extract_industry_data(response)},
                platform_strategies={"content": self._extract_distribution_strategy(response)},
                budget_benchmarks={"content": self._extract_budget_insights(response)},
                market_opportunity_score=market_score,
                competitive_advantage=competitive_advantage,
                market_recommendation=recommendation,
                research_date=datetime.now().isoformat(),
                data_freshness="Current",
                processing_time=processing_time,
                cost=0.01,
                success=True,
                error_message=None
            )
            
            logger.info(f"📊 Perplexity market research complete in {processing_time:.2f}s - Score: {market_score:.1f}/10")
            
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
    
    def _calculate_market_score(self, response: str, genre: str, title: str) -> float:
        """Calculate dynamic market score based on response content"""
        
        base_score = 5.0
        response_lower = response.lower()
        
        # Positive market indicators
        positive_indicators = [
            'strong performance', 'box office success', 'growing market', 'high demand',
            'popular genre', 'trending', 'profitable', 'successful', 'opportunity',
            'favorable conditions', 'strong audience', 'commercial appeal'
        ]
        
        # Negative market indicators
        negative_indicators = [
            'declining market', 'oversaturated', 'poor performance', 'challenging',
            'difficult market', 'limited appeal', 'niche audience', 'risky',
            'competitive pressure', 'market fatigue', 'underperforming'
        ]
        
        # Count indicators
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        # Adjust score based on indicators
        base_score += (positive_count * 0.4) - (negative_count * 0.5)
        
        # Genre-specific adjustments
        if genre.lower() in ['action', 'adventure', 'superhero', 'sci-fi']:
            if any(word in response_lower for word in ['franchise', 'sequel', 'universe']):
                base_score += 0.5
        elif genre.lower() in ['horror', 'thriller']:
            if any(word in response_lower for word in ['low budget', 'high return', 'profitable']):
                base_score += 0.3
        elif genre.lower() in ['drama', 'indie']:
            if any(word in response_lower for word in ['awards', 'festival', 'critical acclaim']):
                base_score += 0.3
        
        # Add content-based randomness for variation
        import hashlib
        content_hash = int(hashlib.md5((response + genre + title).encode()).hexdigest()[:8], 16)
        import random
        random.seed(content_hash % 2147483647)
        variation = (random.random() - 0.5) * 0.6  # ±0.3 variation
        base_score += variation
        
        # Ensure bounds
        return max(1.0, min(10.0, base_score))
    
    def _extract_competitive_advantage(self, response: str) -> str:
        """Extract competitive advantage from response"""
        
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['unique', 'innovative', 'fresh', 'original']):
            return "Strong differentiation potential with unique elements"
        elif any(word in response_lower for word in ['competitive', 'crowded', 'saturated']):
            return "Competitive market requiring strong execution"
        elif any(word in response_lower for word in ['opportunity', 'gap', 'underserved']):
            return "Market opportunity identified for this genre"
        else:
            return "Standard market positioning expected"
    
    def _generate_market_recommendation(self, score: float, response: str) -> str:
        """Generate market recommendation based on score and content"""
        
        if score >= 8.0:
            return "Strong market opportunity - proceed with confidence"
        elif score >= 6.5:
            return "Favorable market conditions - good commercial potential"
        elif score >= 5.0:
            return "Moderate opportunity - careful positioning required"
        elif score >= 3.0:
            return "Challenging market - significant risks to consider"
        else:
            return "Difficult market conditions - high risk investment"
    
    def _extract_competitive_analysis(self, response: str) -> str:
        """Extract competitive analysis section"""
        
        lines = response.split('\n')
        competitive_section = []
        in_competitive = False
        
        for line in lines:
            if any(word in line.lower() for word in ['competitive', 'similar films', 'competition']):
                in_competitive = True
            elif in_competitive and line.strip():
                competitive_section.append(line.strip())
            elif in_competitive and not line.strip() and len(competitive_section) > 3:
                break
        
        return '\n'.join(competitive_section[:10]) if competitive_section else "Competitive analysis included in main research"
    
    def _extract_industry_data(self, response: str) -> str:
        """Extract industry data and trends"""
        
        lines = response.split('\n')
        industry_section = []
        
        for line in lines:
            if any(word in line.lower() for word in ['trend', 'market', 'industry', 'box office', 'performance']):
                industry_section.append(line.strip())
        
        return '\n'.join(industry_section[:8]) if industry_section else "Industry trends analysis included"
    
    def _extract_distribution_strategy(self, response: str) -> str:
        """Extract distribution strategy insights"""
        
        lines = response.split('\n')
        distribution_section = []
        
        for line in lines:
            if any(word in line.lower() for word in ['distribution', 'release', 'platform', 'streaming', 'theatrical']):
                distribution_section.append(line.strip())
        
        return '\n'.join(distribution_section[:6]) if distribution_section else "Distribution strategy recommendations included"
    
    def _extract_budget_insights(self, response: str) -> str:
        """Extract budget and financial insights"""
        
        lines = response.split('\n')
        budget_section = []
        
        for line in lines:
            if any(word in line.lower() for word in ['budget', 'cost', 'financial', 'revenue', 'profit', 'million']):
                budget_section.append(line.strip())
        
        return '\n'.join(budget_section[:5]) if budget_section else "Budget considerations included in analysis"
