#!/usr/bin/env python3
"""
DeepSeek Financial Analysis Integration
Advanced financial modeling, box office prediction, and ROI analysis for screenplay evaluation
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
class DeepSeekResult:
    """DeepSeek financial analysis result with comprehensive modeling"""
    
    # Box Office Prediction
    box_office_prediction: Optional[Dict[str, Any]] = None  # P10/P50/P90 scenarios
    domestic_international_split: Optional[Dict[str, Any]] = None
    seasonal_performance_factors: Optional[Dict[str, Any]] = None
    
    # Budget & ROI Analysis
    budget_optimization: Optional[Dict[str, Any]] = None    # Cost-benefit analysis
    roi_analysis: Optional[Dict[str, Any]] = None           # Return calculations
    investment_scenarios: Optional[Dict[str, Any]] = None   # Different funding levels
    
    # Risk Assessment
    risk_assessment: Optional[Dict[str, Any]] = None        # Statistical risk modeling
    market_volatility: Optional[Dict[str, Any]] = None      # Market condition impacts
    competitive_threats: Optional[Dict[str, Any]] = None    # Competition analysis
    
    # Production Analytics
    production_optimization: Optional[Dict[str, Any]] = None # Scheduling & resources
    cast_roi_analysis: Optional[Dict[str, Any]] = None      # Star power vs cost
    location_cost_analysis: Optional[Dict[str, Any]] = None # Geographic factors
    
    # Distribution Strategy
    release_strategy: Optional[Dict[str, Any]] = None       # Timing optimization
    platform_analysis: Optional[Dict[str, Any]] = None     # Theatrical vs streaming
    marketing_efficiency: Optional[Dict[str, Any]] = None   # Marketing ROI
    
    # Core metrics
    overall_financial_score: float = 0.0  # 0-10 financial viability
    confidence_level: float = 0.0         # Statistical confidence
    recommendation: str = ""              # Investment recommendation
    
    # Processing metadata
    processing_time: float = 0.0
    cost: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    raw_response: str = ""

class DeepSeekAnalyzer:
    """DeepSeek AI integration for advanced financial modeling and box office prediction"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        self.model = "deepseek-reasoner"  # Use reasoning model for financial analysis
        
        # DeepSeek pricing (as of current rates)
        self.input_cost_per_token = 0.00055 / 1000   # $0.55 per 1M input tokens
        self.output_cost_per_token = 0.0022 / 1000   # $2.20 per 1M output tokens
        
        if not self.api_key:
            logger.warning("⚠️  DEEPSEEK_API_KEY not set - DeepSeek financial analysis will be disabled")
        else:
            logger.info("💰 DeepSeek Financial Analyzer initialized")
    
    async def analyze_financial_potential(
        self, 
        screenplay_text: str, 
        title: str, 
        genre: str = "",
        budget_estimate: Optional[float] = None,
        comparable_films: List[str] = None
    ) -> Optional[DeepSeekResult]:
        """Comprehensive financial analysis of screenplay potential"""
        
        if not self.api_key:
            logger.warning("❌ DeepSeek financial analysis skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create comprehensive financial analysis prompt
            prompt = self._create_financial_analysis_prompt(
                screenplay_text, title, genre, budget_estimate, comparable_films or []
            )
            
            # Call DeepSeek API
            response = await self._call_deepseek_api(prompt)
            
            # Parse response
            analysis_data = self._parse_financial_response(response)
            
            # Calculate cost
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
            
            processing_time = time.time() - start_time
            
            result = DeepSeekResult(
                box_office_prediction=analysis_data.get('box_office_prediction'),
                domestic_international_split=analysis_data.get('domestic_international_split'),
                seasonal_performance_factors=analysis_data.get('seasonal_performance_factors'),
                budget_optimization=analysis_data.get('budget_optimization'),
                roi_analysis=analysis_data.get('roi_analysis'),
                investment_scenarios=analysis_data.get('investment_scenarios'),
                risk_assessment=analysis_data.get('risk_assessment_detailed', analysis_data.get('risk_assessment')),
                market_volatility=analysis_data.get('market_volatility'),
                competitive_threats=analysis_data.get('competitive_threats'),
                production_optimization=analysis_data.get('production_optimization'),
                cast_roi_analysis=analysis_data.get('cast_roi_analysis'),
                location_cost_analysis=analysis_data.get('location_cost_analysis'),
                release_strategy=analysis_data.get('release_strategy'),
                platform_analysis=analysis_data.get('platform_analysis'),
                marketing_efficiency=analysis_data.get('marketing_efficiency'),
                overall_financial_score=analysis_data.get('overall_financial_score', 0.0),
                confidence_level=analysis_data.get('confidence_level', 0.0),
                recommendation=analysis_data.get('executive_summary', {}).get('bottom_line_recommendation', analysis_data.get('recommendation', 'Insufficient data')),
                processing_time=processing_time,
                cost=cost,
                success=True,
                error_message=None,
                raw_response=response
            )
            
            logger.info(f"💰 DeepSeek financial analysis complete in {processing_time:.2f}s")
            logger.info(f"📊 Financial Score: {result.overall_financial_score}/10")
            logger.info(f"💵 Cost: ${cost:.4f}")
            
            return result
            
        except Exception as e:
            error_str = str(e)
            processing_time = time.time() - start_time
            
            # Check if it's a timeout error - provide fallback analysis
            if "timeout" in error_str.lower() or "timed out" in error_str.lower() or processing_time > 120:
                logger.warning(f"⚠️ DeepSeek API timeout ({processing_time:.1f}s) - providing fallback analysis")
                
                # Provide a reasonable fallback score based on genre
                fallback_score = self._get_fallback_score(genre)
                
                return DeepSeekResult(
                    overall_financial_score=fallback_score,
                    confidence_level=0.3,  # Low confidence for fallback
                    recommendation=f'Fallback analysis (API timeout): {genre} films typically score {fallback_score}/10 for financial viability',
                    processing_time=processing_time,
                    cost=0.0,
                    success=True,  # Mark as success so it gets saved
                    error_message=f"API timeout after {processing_time:.1f}s - fallback analysis provided",
                    raw_response="Fallback analysis due to API timeout"
                )
            else:
                logger.error(f"❌ DeepSeek financial analysis failed: {e}")
                
                return DeepSeekResult(
                    overall_financial_score=3.0,  # Default middle score
                    confidence_level=0.2,
                    recommendation='Analysis failed - manual review recommended',
                    processing_time=processing_time,
                    cost=0.0,
                    success=True,  # Mark as success so it gets saved
                    error_message=str(e),
                    raw_response=""
                )
    
    def _create_financial_analysis_prompt(
        self, 
        screenplay_text: str, 
        title: str, 
        genre: str,
        budget_estimate: Optional[float],
        comparable_films: List[str]
    ) -> str:
        """Create comprehensive financial analysis prompt for DeepSeek"""
        
        # Extract key elements from screenplay for analysis
        screenplay_sample = screenplay_text[:8000]  # First 8k characters for analysis
        
        budget_context = f"Estimated budget: ${budget_estimate:,.0f}" if budget_estimate else "Budget: To be determined"
        comparables_context = f"Comparable films: {', '.join(comparable_films)}" if comparable_films else "No specific comparables provided"
        
        return f"""You are a Hollywood financial analyst explaining movie investments to smart film enthusiasts. Your job is to break down complex financial concepts into clear, understandable explanations while being thorough and accurate.

SCREENPLAY: "{title}"
GENRE: {genre}
{budget_context}
{comparables_context}

SCREENPLAY CONTENT (SAMPLE):
{screenplay_sample}

IMPORTANT CONTEXT:
- The budget provided is the PRODUCTION budget (what it costs to make the movie)
- Break-even requires covering production + marketing + distribution costs
- Theaters typically keep 50% of ticket sales, studios get the other 50%
- Modern movies make money from multiple sources: theaters, streaming, TV, international sales, merchandise

ANALYSIS REQUIREMENTS:
1. Explain ALL financial terms in simple language (like explaining to a smart 14-year-old)
2. Include both theatrical AND streaming/digital scenarios
3. Show your work - explain HOW you calculated each number
4. Make risk assessments clear and actionable
5. Consider modern distribution models (Netflix deals, day-and-date streaming, etc.)

RESPOND WITH VALID JSON:
{{
    "box_office_prediction": {{
        "conservative_scenario": number,  // Worst case realistic outcome (10% chance of doing worse)
        "expected_scenario": number,      // Most likely outcome (50/50 chance)
        "optimistic_scenario": number,    // Best case realistic outcome (10% chance of doing better)
        "confidence_interval": "string",  // How sure we are about these numbers
        "methodology_explanation": "string", // EXPLAIN: How did you calculate these predictions? What movies did you compare to?
        "why_these_numbers": "string"     // EXPLAIN: Why this specific range? What factors drive the prediction?
    }},
    "domestic_international_split": {{
        "domestic_percentage": number,    // US/Canada market share
        "international_percentage": number, // International market share
        "key_international_markets": ["list"], // Top international markets
        "currency_risk_factors": "string" // Exchange rate considerations
    }},
    "seasonal_performance_factors": {{
        "optimal_release_window": "string", // Best release timing
        "seasonal_multiplier": number,      // Seasonal performance factor
        "competition_density": "string",    // Competition analysis
        "holiday_impact": "string"          // Holiday performance factors
    }},
    "budget_optimization": {{
        "recommended_budget_range": {{
            "minimum": number,
            "optimal": number,
            "maximum": number
        }},
        "cost_allocation_recommendations": {{
            "above_line": number,     // Cast, director, producer costs
            "below_line": number,     // Production costs
            "post_production": number, // Post-production costs
            "marketing": number       // Marketing budget recommendation
        }},
        "efficiency_opportunities": ["list"] // Cost optimization strategies
    }},
    "roi_analysis": {{
        "break_even_point": number,        // Total box office revenue needed to break even
        "break_even_explanation": "string", // EXPLAIN: Why this number? Show the math: production + marketing + theater split
        "expected_roi_percentage": number, // How much profit as percentage of investment
        "roi_explanation": "string",       // EXPLAIN: What ROI means - if you invest $100 and get 50% ROI, you make $50 profit
        "payback_period_months": number,   // How many months to get your money back
        "payback_explanation": "string",   // EXPLAIN: What payback period means and why this timeline
        "net_present_value": number,       // NPV calculation (today's value of future profits)
        "npv_explanation": "string",       // EXPLAIN: NPV in simple terms - is this investment worth it vs putting money in the bank?
        "internal_rate_return": number,    // IRR percentage (annual return rate)
        "irr_explanation": "string"        // EXPLAIN: IRR like interest rate - what annual return this investment gives you
    }},
    "investment_scenarios": {{
        "low_budget_scenario": {{
            "budget": number,
            "expected_return": number,
            "risk_level": "string"
        }},
        "medium_budget_scenario": {{
            "budget": number,
            "expected_return": number,
            "risk_level": "string"
        }},
        "high_budget_scenario": {{
            "budget": number,
            "expected_return": number,
            "risk_level": "string"
        }}
    }},
    "risk_assessment": {{
        "overall_risk_score": number,      // 1-10 risk rating
        "key_risk_factors": ["list"],      // Primary risk elements
        "mitigation_strategies": ["list"], // Risk reduction approaches
        "insurance_recommendations": "string", // Insurance considerations
        "contingency_percentage": number   // Recommended contingency fund
    }},
    "market_volatility": {{
        "genre_stability": "string",       // Genre market stability
        "economic_sensitivity": "string",  // Economic downturn impact
        "streaming_impact": "string",      // Streaming vs theatrical
        "demographic_shifts": "string"     // Audience trend impacts
    }},
    "competitive_threats": {{
        "similar_projects_in_development": "string",
        "market_saturation_risk": "string",
        "franchise_competition": "string",
        "timing_vulnerabilities": "string"
    }},
    "production_optimization": {{
        "optimal_shooting_schedule": "string", // Scheduling recommendations
        "location_cost_efficiency": "string",  // Location strategy
        "crew_size_optimization": "string",    // Crew efficiency
        "equipment_rental_strategy": "string"  // Equipment optimization
    }},
    "cast_roi_analysis": {{
        "star_power_impact": "string",     // Celebrity casting impact
        "cost_benefit_ratios": "string",   // Cast cost vs box office draw
        "ensemble_vs_lead_strategy": "string", // Casting strategy
        "international_appeal_factors": "string" // Global star power
    }},
    "location_cost_analysis": {{
        "cost_effective_locations": ["list"], // Budget-friendly locations
        "tax_incentive_opportunities": ["list"], // Available tax credits
        "logistical_cost_factors": "string",     // Transportation, housing
        "production_value_optimization": "string" // Visual value vs cost
    }},
    "release_strategy": {{
        "optimal_release_date": "string",     // Recommended release timing
        "platform_strategy": "string",        // Theatrical vs streaming
        "rollout_recommendations": "string",  // Release pattern
        "awards_season_considerations": "string" // Awards strategy impact
    }},
    "platform_analysis": {{
        "theatrical_revenue_potential": number, // Traditional movie theater revenue
        "streaming_revenue_potential": number,   // Netflix/Amazon/Apple TV+ deals
        "vod_revenue_potential": number,         // Video-on-demand rentals/purchases
        "international_sales_potential": number, // Foreign market sales
        "ancillary_revenue_streams": ["list"],   // TV, merchandise, etc.
        "platform_strategy_explanation": "string", // EXPLAIN: Which distribution method is best for this movie and why?
        "streaming_deal_scenarios": {{
            "netflix_acquisition_estimate": number, // Estimated Netflix purchase price
            "day_and_date_streaming": number,       // Simultaneous theater + streaming revenue
            "streaming_exclusive_value": number,    // Value if it goes streaming-only
            "streaming_explanation": "string"       // EXPLAIN: How streaming deals work vs theatrical
        }},
        "modern_distribution_reality": "string" // EXPLAIN: How movies actually make money in 2024+ (not just theaters)
    }},
    "marketing_efficiency": {{
        "recommended_marketing_spend": number,
        "cost_per_acquisition": number,
        "roi_by_marketing_channel": "string",
        "viral_potential_score": number,
        "social_media_strategy": "string"
    }},
    "risk_assessment_detailed": {{
        "overall_risk_score": number,      // 0-10 (0=very risky, 10=very safe)
        "risk_score_explanation": "string", // EXPLAIN: How did you calculate this risk score? What makes it risky/safe?
        "major_risk_factors": ["list"],     // Top 3-5 things that could go wrong
        "risk_mitigation_strategies": ["list"], // How to reduce these risks
        "comparable_film_performance": "string", // EXPLAIN: How did similar movies perform financially?
        "market_conditions_impact": "string"     // EXPLAIN: How current market affects this movie's chances
    }},
    "overall_financial_score": number,     // 0-10 overall financial viability score
    "financial_score_breakdown": {{
        "score_explanation": "string",     // EXPLAIN: Why this score? What factors went into it?
        "profit_probability": number,      // 0-100% chance this movie will be profitable
        "loss_probability": number,        // 0-100% chance this movie will lose money
        "breakout_hit_probability": number, // 0-100% chance this becomes a surprise success
        "what_score_means": "string"       // EXPLAIN: What does a 7/10 vs 4/10 financial score actually mean?
    }},
    "executive_summary": {{
        "bottom_line_recommendation": "string", // CLEAR: Should you invest in this movie? Yes/No and why?
        "best_case_scenario": "string",         // EXPLAIN: If everything goes right, what happens?
        "worst_case_scenario": "string",        // EXPLAIN: If everything goes wrong, what happens?
        "most_likely_outcome": "string",        // EXPLAIN: What will probably actually happen?
        "key_success_factors": ["list"],        // Top 3 things that need to go right for success
        "deal_breakers": ["list"]               // Top 3 things that would make this a bad investment
    }},
    "confidence_level": number,            // 0-1 how confident we are in this analysis
    "confidence_explanation": "string"     // EXPLAIN: Why are we confident/not confident in these predictions?
}}

ANALYSIS GUIDELINES:
- Use statistical modeling and data-driven projections
- Consider current market conditions and trends
- ALWAYS fill in every "_explanation" field with clear, simple explanations
- Assume the reader is smart but doesn't know film finance jargon
- Show your math wherever possible (e.g., "$25M production + $15M marketing = $40M total cost")
- Include specific examples and comparisons to real movies when possible
- Make risk assessments actionable - what can be done to improve odds?
- Consider both traditional theatrical and modern streaming distribution models
- Be honest about uncertainty - explain what could change these projections

IMPORTANT: Every explanation field must be filled with substantial, helpful content. Don't just restate the number - explain WHY and HOW.
- Factor in genre-specific performance patterns
- Include risk-adjusted returns and sensitivity analysis
- Provide actionable financial recommendations
- Base projections on comparable film performance data
- Consider both theatrical and streaming revenue models
- Account for international market variations
- Include contingency planning and risk mitigation

Provide comprehensive, mathematically sound financial analysis with clear reasoning and statistical confidence measures."""
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """Call DeepSeek API for financial analysis"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a world-class Hollywood financial analyst and data scientist with expertise in box office prediction, film finance, and statistical modeling. You provide mathematically rigorous, data-driven financial analysis for film investments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent financial analysis
                "max_completion_tokens": 4000,
                "response_format": {"type": "json_object"}
            }
            
            # Use reasonable timeout - fallback if DeepSeek takes too long
            timeout = httpx.Timeout(connect=30.0, read=90.0, write=30.0, pool=30.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('choices') and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        raise Exception("No response content from DeepSeek")
                else:
                    error_text = response.text
                    raise Exception(f"DeepSeek API error {response.status_code}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ DeepSeek API call failed: {e}")
            raise
    
    def _parse_financial_response(self, response: str) -> Dict[str, Any]:
        """Parse DeepSeek financial analysis response"""
        
        try:
            # Clean the response
            response = response.strip()
            
            # Handle potential JSON truncation issues
            if response and not response.endswith('}'):
                # Try to find the last complete object
                last_brace = response.rfind('}')
                if last_brace > 0:
                    response = response[:last_brace + 1]
                else:
                    # If no closing brace found, add one
                    response += '}'
            
            # Parse JSON
            data = json.loads(response)
            
            # Calculate overall financial score from available data if missing
            if 'overall_financial_score' not in data:
                score = self._calculate_financial_score(data)
                data['overall_financial_score'] = score
                logger.info(f"💰 Calculated financial score: {score}/10 from available data")
            
            if 'confidence_level' not in data:
                data['confidence_level'] = 0.7  # Higher confidence since we have detailed analysis
            
            if 'recommendation' not in data:
                # Generate recommendation based on score
                score = data['overall_financial_score']
                if score >= 8.0:
                    data['recommendation'] = 'Highly recommended for investment'
                elif score >= 6.0:
                    data['recommendation'] = 'Recommended with moderate risk'
                elif score >= 4.0:
                    data['recommendation'] = 'Consider with caution'
                else:
                    data['recommendation'] = 'High risk investment'
            
            # Ensure numerical fields are properly typed
            data['overall_financial_score'] = float(data.get('overall_financial_score', 5.0))
            data['confidence_level'] = max(0.0, min(1.0, float(data.get('confidence_level', 0.7))))
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse DeepSeek JSON response: {e}")
            logger.error(f"Raw response: {response}")
            
            # Return default structure with minimal score
            return {
                'overall_financial_score': 3.0,
                'confidence_level': 0.3,
                'recommendation': 'Analysis incomplete - requires manual review'
            }
    
    def _calculate_financial_score(self, data: Dict[str, Any]) -> float:
        """Calculate financial score from available analysis data"""
        
        score = 5.0  # Base score
        
        try:
            # ROI Analysis scoring (0-3 points)
            roi_data = data.get('roi_analysis', {})
            if roi_data:
                roi_percentage = roi_data.get('expected_roi_percentage', 0)
                if roi_percentage >= 20:
                    score += 3.0
                elif roi_percentage >= 10:
                    score += 2.0
                elif roi_percentage >= 5:
                    score += 1.0
            
            # Box Office Prediction scoring (0-2 points)
            box_office = data.get('box_office_prediction', {})
            if box_office:
                expected_revenue = box_office.get('expected_scenario', 0)
                if expected_revenue >= 100_000_000:  # $100M+
                    score += 2.0
                elif expected_revenue >= 50_000_000:   # $50M+
                    score += 1.0
            
            # Risk Assessment scoring (-2 to +1 points)
            risk_data = data.get('risk_assessment', {})
            if risk_data:
                risk_score = risk_data.get('overall_risk_score', 5)
                if risk_score <= 3:      # Low risk
                    score += 1.0
                elif risk_score >= 8:    # High risk
                    score -= 2.0
                elif risk_score >= 6:    # Medium-high risk
                    score -= 1.0
            
            # Budget Optimization scoring (0-1 points)
            budget_data = data.get('budget_optimization', {})
            if budget_data and budget_data.get('recommended_budget_range'):
                # If we have detailed budget analysis, add confidence
                score += 0.5
            
            # Ensure score is within bounds
            score = max(0.0, min(10.0, score))
            
            logger.info(f"💰 Financial score calculation: ROI={roi_data.get('expected_roi_percentage', 'N/A')}%, "
                       f"Box Office=${box_office.get('expected_scenario', 'N/A')}, "
                       f"Risk={risk_data.get('overall_risk_score', 'N/A')}/10 → Score={score:.1f}/10")
            
            return score
            
        except Exception as e:
            logger.warning(f"⚠️  Error calculating financial score: {e}")
            return 5.0  # Default middle score
    
    def _get_fallback_score(self, genre: str) -> float:
        """Get fallback financial score based on genre"""
        
        # Genre-based fallback scores (based on typical financial performance)
        genre_scores = {
            'action': 6.5,
            'adventure': 6.0,
            'comedy': 5.5,
            'drama': 4.5,
            'horror': 6.0,
            'thriller': 5.5,
            'sci-fi': 6.0,
            'fantasy': 6.5,
            'romance': 4.0,
            'documentary': 3.0,
            'animation': 7.0,
            'family': 6.5,
            'mystery': 5.0,
            'crime': 5.5,
            'war': 4.5,
            'western': 4.0,
            'musical': 4.5,
            'biography': 4.0
        }
        
        # Normalize genre to lowercase for matching
        genre_lower = genre.lower() if genre else 'drama'
        
        # Find best match
        for key, score in genre_scores.items():
            if key in genre_lower:
                return score
        
        # Default fallback
        return 5.0
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for cost calculation"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def to_database_format(self, result: DeepSeekResult) -> Dict[str, Any]:
        """Convert DeepSeekResult to database format"""
        return {
            'deepseek_box_office_prediction': json.dumps(result.box_office_prediction) if result.box_office_prediction else None,
            'deepseek_budget_optimization': json.dumps(result.budget_optimization) if result.budget_optimization else None,
            'deepseek_roi_analysis': json.dumps(result.roi_analysis) if result.roi_analysis else None,
            'deepseek_risk_assessment': json.dumps(result.risk_assessment) if result.risk_assessment else None,
            'deepseek_production_optimization': json.dumps(result.production_optimization) if result.production_optimization else None,
            'deepseek_platform_analysis': json.dumps(result.platform_analysis) if getattr(result, 'platform_analysis', None) else None,
            'deepseek_financial_score': float(result.overall_financial_score) if result.overall_financial_score is not None else None,
            'deepseek_confidence': float(result.confidence_level) if result.confidence_level is not None else None,
            'deepseek_recommendation': str(result.recommendation) if result.recommendation else None,
            'deepseek_cost': float(result.cost) if result.cost is not None else None,
            'deepseek_processing_time': float(result.processing_time) if result.processing_time is not None else None,
            'deepseek_success': bool(result.success) if result.success is not None else None,
            'deepseek_error_message': str(result.error_message) if result.error_message else None,
            'deepseek_raw_response': str(result.raw_response) if result.raw_response else None
        }
