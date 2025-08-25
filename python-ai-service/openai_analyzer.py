#!/usr/bin/env python3
"""
OpenAI ChatGPT-5 Screenplay Analyzer
Provides third AI evaluation alongside Claude Opus 4.1 and Grok 4
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
from dotenv import load_dotenv
from budget_utils import format_budget_context_for_ai, estimate_budget_from_screenplay, get_casting_suggestions_by_budget

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OpenAIResult:
    """OpenAI ChatGPT-5 analysis result"""
    score: float  # 0-10
    recommendation: str  # "Pass", "Consider", "Recommend", "Strong Recommend"
    verdict: str  # One-line assessment
    processing_time: float
    cost: float
    confidence: float
    raw_response: str
    
    # OpenAI-specific insights
    commercial_assessment: Optional[Dict[str, Any]] = None
    technical_craft: Optional[Dict[str, Any]] = None
    industry_comparison: Optional[Dict[str, Any]] = None
    
    # Hollywood Movie Poster Generation
    movie_poster_url: Optional[str] = None
    poster_generation_prompt: Optional[str] = None

class OpenAIAnalyzer:
    """OpenAI ChatGPT-5 API integration for screenplay analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.dalle_url = "https://api.openai.com/v1/images/generations"
        
        # Try GPT-5 first, fallback to GPT-4o if not available
        self.model = os.getenv("OPENAI_MODEL", "gpt-5")  # Default to GPT-5
        self.fallback_model = "gpt-4o"
        
        # Hollywood Movie Poster Generation
        self.poster_generation_enabled = True
        self.dalle_model = "dall-e-3"  # Use DALL-E 3 for high-quality posters
        
        # OpenAI pricing (estimated for GPT-5, actual for GPT-4o)
        if self.model == "gpt-5":
            self.input_cost_per_token = 0.00001   # $0.01 per 1K tokens (estimated GPT-5 pricing)
            self.output_cost_per_token = 0.00003  # $0.03 per 1K tokens (estimated GPT-5 pricing)
        else:
            self.input_cost_per_token = 0.000005   # $0.005 per 1K tokens for GPT-4o
            self.output_cost_per_token = 0.000015  # $0.015 per 1K tokens for GPT-4o
        
        if not self.api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set - OpenAI analysis will be disabled")
        else:
            logger.info(f"🤖 OpenAI {self.model.upper()} Analyzer initialized")
    
    async def analyze(self, screenplay_text: str, title: str, genre: str = "", budget_estimate: Optional[float] = None) -> Optional[OpenAIResult]:
        """Analyze screenplay with OpenAI ChatGPT-5 (with GPT-4o fallback)"""
        
        if not self.api_key:
            logger.warning("❌ OpenAI analysis skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create focused prompt for OpenAI
            prompt = self._create_prompt(screenplay_text, title, genre, budget_estimate)
            
            # Call OpenAI API with fallback logic
            response = await self._call_openai_api_with_fallback(prompt)
            
            # Parse response
            analysis_data = self._parse_response(response)
            
            # Calculate cost (estimate tokens)
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
            
            processing_time = time.time() - start_time
            
            # Generate Hollywood movie poster if enabled
            poster_url = None
            poster_prompt = None
            if self.poster_generation_enabled and self.api_key:
                try:
                    poster_url, poster_prompt = await self._generate_movie_poster(title, genre, analysis_data)
                    if poster_url:
                        logger.info(f"🎬 Hollywood movie poster generated successfully with DALL-E 3")
                        # Add poster generation cost to total cost
                        cost += 0.04  # DALL-E 3 standard cost per image
                    else:
                        logger.warning(f"⚠️  Poster generation failed - no image URL returned")
                except Exception as e:
                    logger.warning(f"⚠️  Poster generation failed: {e}")
            
            result = OpenAIResult(
                score=analysis_data.get('score', 0.0),
                recommendation=analysis_data.get('recommendation', 'Pass'),
                verdict=analysis_data.get('verdict', 'Analysis incomplete'),
                processing_time=processing_time,
                cost=cost,
                confidence=analysis_data.get('confidence', 0.5),
                raw_response=response,
                commercial_assessment=analysis_data.get('commercial_assessment'),
                technical_craft=analysis_data.get('technical_craft'),
                industry_comparison=analysis_data.get('industry_comparison'),
                movie_poster_url=poster_url,
                poster_generation_prompt=poster_prompt
            )
            
            logger.info(f"🤖 OpenAI analysis completed in {processing_time:.2f}s")
            logger.info(f"💰 OpenAI cost: ${cost:.4f}")
            logger.info(f"⭐ OpenAI score: {result.score}/10 ({result.recommendation})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ OpenAI analysis failed: {e}")
            return None
    
    def _create_prompt(self, screenplay_text: str, title: str, genre: str, budget_estimate: Optional[float] = None) -> str:
        """Create comprehensive prompt for OpenAI ChatGPT-4o"""
        
        # Truncate if too long (OpenAI has context limits)
        max_chars = 60000  # Conservative limit for GPT-4o
        if len(screenplay_text) > max_chars:
            screenplay_text = screenplay_text[:max_chars] + "\n\n[TRUNCATED FOR ANALYSIS]"
        
        # Enhanced budget context with AI estimation
        estimated_budget = None
        if not budget_estimate:
            estimated_budget = estimate_budget_from_screenplay(screenplay_text, title, genre or "Drama")
        
        budget_context = format_budget_context_for_ai(budget_estimate, estimated_budget)
        
        # Get budget-appropriate casting suggestions for commercial analysis
        budget_for_casting = budget_estimate or estimated_budget[1] if estimated_budget else 10_000_000
        casting_strategy = get_casting_suggestions_by_budget(budget_for_casting, genre or "Drama")

        return f"""You are a seasoned Hollywood script reader and development executive with 15+ years of experience evaluating screenplays for major studios. Your job is to provide a comprehensive, industry-standard analysis that focuses on commercial viability and technical craft.

**SCREENPLAY: "{title}"**
{f"**GENRE: {genre}**" if genre else ""}
{budget_context}

**SCREENPLAY TEXT:**
{screenplay_text}

**ANALYSIS FRAMEWORK:**

## **COMMERCIAL ASSESSMENT**
Evaluate market potential and audience appeal:
1. **High Concept Appeal**: Is this a clear, marketable premise that can be pitched in one sentence?
2. **Target Demographics**: Who is the core audience and how large is that market?
3. **Budget Considerations**: What's the realistic production budget range and ROI potential?
4. **Franchise Potential**: Could this spawn sequels, prequels, or expanded universe content?
5. **International Appeal**: How well would this translate globally?

## **TECHNICAL CRAFT EVALUATION**
Assess professional screenplay standards:
1. **Structure Adherence**: How well does it follow three-act structure and industry pacing?
2. **Character Development**: Are characters well-defined with clear arcs and motivations?
3. **Dialogue Quality**: Is the dialogue natural, character-specific, and purposeful?
4. **Visual Storytelling**: Does it effectively use cinematic language and show vs. tell?
5. **Genre Execution**: How well does it deliver on genre expectations and conventions?

## **INDUSTRY COMPARISON**
Compare against successful films:
1. **Comparable Titles**: What successful films does this most resemble?
2. **Competitive Advantage**: What makes this stand out in a crowded marketplace?
3. **Timing Assessment**: Is this the right concept for the current market climate?
4. **Studio Fit**: Which studios or production companies would be most interested?

**RESPONSE FORMAT:**
Provide analysis as JSON with these exact keys:
{{
    "score": 0.0,
    "recommendation": "",
    "verdict": "",
    "confidence": 0.0,
    "commercial_assessment": {{
        "high_concept_score": 0,
        "target_demographics": "",
        "budget_range": "",
        "franchise_potential": "",
        "international_appeal": ""
    }},
    "technical_craft": {{
        "structure_score": 0,
        "character_development": "",
        "dialogue_quality": "",
        "visual_storytelling": "",
        "genre_execution": ""
    }},
    "industry_comparison": {{
        "comparable_titles": [],
        "competitive_advantage": "",
        "market_timing": "",
        "studio_recommendations": []
    }}
}}

**SCORING GUIDE:**
- 9-10: Exceptional, ready for A-list talent and major studio (rare - only truly outstanding scripts)
- 7-8: Strong commercial potential, minor polish needed for production
- 5-6: Promising concept, needs significant development work
- 3-4: Weak execution, major rewrites required before consideration
- 1-2: Not viable in current form, fundamental issues

**IMPORTANT:** Be honest and realistic with scoring. Most scripts fall in the 3-7 range. Only exceptional work deserves 8+. Consider commercial viability, craft quality, and market competition. Avoid defaulting to middle scores - differentiate based on actual quality.

**RECOMMENDATION GUIDE:**
- "Strong Recommend": 8.5+ score, immediate greenlight potential
- "Recommend": 7.0-8.4 score, strong with minor notes
- "Consider": 5.0-6.9 score, has potential but needs work
- "Pass": Below 5.0, not ready for development

**TONE:** Professional, industry-focused, and constructive. Think like a studio executive who needs to justify decisions to investors and marketing teams."""

    async def _call_openai_api_with_fallback(self, prompt: str) -> str:
        """Call OpenAI API with GPT-5 first, fallback to GPT-4o if needed"""
        
        # Try GPT-5 first
        try:
            return await self._call_openai_api(prompt, self.model)
        except Exception as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                logger.warning(f"⚠️  {self.model} not available, falling back to {self.fallback_model}")
                # Update pricing for fallback model
                self.input_cost_per_token = 0.000005   # GPT-4o pricing
                self.output_cost_per_token = 0.000015  # GPT-4o pricing
                return await self._call_openai_api(prompt, self.fallback_model)
            else:
                raise e

    async def _call_openai_api(self, prompt: str, model: str = None) -> str:
        """Call OpenAI API with error handling"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional Hollywood script reader and development executive with extensive industry experience."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_completion_tokens": 2500,
            "temperature": 1.0,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                raise Exception("Invalid OpenAI API response format")
            
            return data['choices'][0]['message']['content']
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured data"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Validate and structure the response
                return self._validate_response(parsed_data)
            else:
                # Fallback parsing if no JSON found
                logger.warning("⚠️  No JSON found in OpenAI response, using fallback parsing")
                return self._fallback_parse(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON parsing failed: {e}, using fallback")
            return self._fallback_parse(response)
    
    def _validate_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure the OpenAI response"""
        
        # Calculate dynamic score if not provided
        raw_score = data.get('score')
        if raw_score is None or raw_score == 0:
            # Calculate score based on available analysis data
            calculated_score = self._calculate_dynamic_score(data)
            logger.info(f"📊 OpenAI score calculated dynamically: {calculated_score:.1f}/10")
        else:
            calculated_score = float(raw_score)
        
        # Ensure basic fields exist
        validated = {
            'score': min(10.0, max(0.0, calculated_score)),
            'recommendation': data.get('recommendation', self._get_recommendation_from_score(calculated_score)),
            'verdict': data.get('verdict', 'Analysis completed'),
            'confidence': min(1.0, max(0.0, data.get('confidence', 0.7)))
        }
        
        # Validate commercial assessment
        if 'commercial_assessment' in data:
            commercial = data['commercial_assessment']
            validated['commercial_assessment'] = {
                'high_concept_score': min(10, max(1, commercial.get('high_concept_score', 5))),
                'target_demographics': commercial.get('target_demographics', 'General audience'),
                'budget_range': commercial.get('budget_range', 'Mid-budget'),
                'franchise_potential': commercial.get('franchise_potential', 'Limited'),
                'international_appeal': commercial.get('international_appeal', 'Moderate')
            }
        
        # Validate technical craft
        if 'technical_craft' in data:
            craft = data['technical_craft']
            validated['technical_craft'] = {
                'structure_score': min(10, max(1, craft.get('structure_score', 5))),
                'character_development': craft.get('character_development', 'Adequate character work'),
                'dialogue_quality': craft.get('dialogue_quality', 'Functional dialogue'),
                'visual_storytelling': craft.get('visual_storytelling', 'Standard visual approach'),
                'genre_execution': craft.get('genre_execution', 'Meets genre expectations')
            }
        
        # Validate industry comparison
        if 'industry_comparison' in data:
            industry = data['industry_comparison']
            validated['industry_comparison'] = {
                'comparable_titles': industry.get('comparable_titles', []),
                'competitive_advantage': industry.get('competitive_advantage', 'Standard approach'),
                'market_timing': industry.get('market_timing', 'Neutral timing'),
                'studio_recommendations': industry.get('studio_recommendations', [])
            }
        
        return validated
    
    def _calculate_dynamic_score(self, data: Dict[str, Any]) -> float:
        """Calculate a dynamic score based on analysis components"""
        
        base_score = 4.0  # Start lower than 5.0 for more variation
        
        try:
            # Commercial Assessment scoring (0-3 points)
            commercial = data.get('commercial_assessment', {})
            if commercial:
                high_concept = commercial.get('high_concept_score', 5)
                if high_concept >= 8:
                    base_score += 2.5
                elif high_concept >= 6:
                    base_score += 1.5
                elif high_concept >= 4:
                    base_score += 0.5
                
                # Franchise potential bonus
                franchise = commercial.get('franchise_potential', '').lower()
                if 'high' in franchise or 'strong' in franchise:
                    base_score += 1.0
                elif 'moderate' in franchise or 'medium' in franchise:
                    base_score += 0.5
                
                # International appeal bonus
                international = commercial.get('international_appeal', '').lower()
                if 'high' in international or 'strong' in international:
                    base_score += 0.5
            
            # Technical Craft scoring (0-2 points)
            craft = data.get('technical_craft', {})
            if craft:
                structure = craft.get('structure_score', 5)
                if structure >= 8:
                    base_score += 1.5
                elif structure >= 6:
                    base_score += 1.0
                elif structure >= 4:
                    base_score += 0.5
                
                # Quality indicators
                dialogue = craft.get('dialogue_quality', '').lower()
                if any(word in dialogue for word in ['excellent', 'outstanding', 'exceptional']):
                    base_score += 0.5
                elif any(word in dialogue for word in ['good', 'strong', 'solid']):
                    base_score += 0.25
            
            # Industry Comparison scoring (0-1 points)
            industry = data.get('industry_comparison', {})
            if industry:
                advantage = industry.get('competitive_advantage', '').lower()
                if any(word in advantage for word in ['unique', 'innovative', 'fresh', 'original']):
                    base_score += 1.0
                elif any(word in advantage for word in ['strong', 'solid', 'good']):
                    base_score += 0.5
                
                timing = industry.get('market_timing', '').lower()
                if 'perfect' in timing or 'ideal' in timing:
                    base_score += 0.5
            
            # Add some randomness for more realistic variation (±0.3)
            import random
            random.seed(hash(str(data)) % 2147483647)  # Consistent randomness based on data
            variation = (random.random() - 0.5) * 0.6  # -0.3 to +0.3
            base_score += variation
            
            # Ensure score is within bounds
            final_score = max(1.0, min(10.0, base_score))
            
            logger.info(f"💰 Dynamic score calculation: Commercial={commercial.get('high_concept_score', 'N/A')}, "
                       f"Structure={craft.get('structure_score', 'N/A')}, "
                       f"Advantage={len(industry.get('competitive_advantage', ''))>0} → Score={final_score:.1f}/10")
            
            return final_score
            
        except Exception as e:
            logger.warning(f"⚠️  Error in dynamic scoring: {e}, using base score")
            return 4.5  # Slightly below middle for failed calculations
    
    def _get_recommendation_from_score(self, score: float) -> str:
        """Get recommendation based on calculated score"""
        if score >= 8.5:
            return "Strong Recommend"
        elif score >= 7.0:
            return "Recommend"
        elif score >= 5.0:
            return "Consider"
        else:
            return "Pass"
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        
        import re
        
        # Try to extract score using regex
        score_match = re.search(r'score["\s:]*(\d+\.?\d*)', response, re.IGNORECASE)
        
        if score_match:
            score = float(score_match.group(1))
        else:
            # Use content-based scoring when no explicit score found
            score = self._analyze_text_for_score(response)
            logger.info(f"📊 Fallback text analysis score: {score:.1f}/10")
        
        # Determine recommendation based on score
        recommendation = self._get_recommendation_from_score(score)
        
        # Extract verdict (first meaningful sentence)
        lines = response.split('\n')
        verdict = next((line.strip() for line in lines if len(line.strip()) > 20), "Analysis completed")
        
        return {
            'score': score,
            'recommendation': recommendation,
            'verdict': verdict[:200],  # Limit length
            'confidence': 0.6  # Lower confidence for fallback parsing
        }
    
    def _analyze_text_for_score(self, text: str) -> float:
        """Analyze response text to estimate a score when no explicit score is provided"""
        
        text_lower = text.lower()
        base_score = 4.0
        
        # Positive indicators
        positive_words = [
            'excellent', 'outstanding', 'exceptional', 'brilliant', 'masterful',
            'compelling', 'engaging', 'strong', 'solid', 'well-crafted',
            'innovative', 'fresh', 'unique', 'original', 'captivating'
        ]
        
        # Negative indicators  
        negative_words = [
            'weak', 'poor', 'lacking', 'problematic', 'confusing', 'unclear',
            'clichéd', 'predictable', 'boring', 'unoriginal', 'derivative',
            'needs work', 'requires revision', 'major issues'
        ]
        
        # Commercial indicators
        commercial_positive = [
            'marketable', 'commercial appeal', 'box office', 'franchise potential',
            'broad audience', 'mass appeal', 'profitable', 'bankable'
        ]
        
        commercial_negative = [
            'niche', 'limited appeal', 'difficult to market', 'risky investment',
            'narrow audience', 'uncommercial'
        ]
        
        # Count positive indicators
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        commercial_pos = sum(1 for phrase in commercial_positive if phrase in text_lower)
        commercial_neg = sum(1 for phrase in commercial_negative if phrase in text_lower)
        
        # Adjust score based on indicators
        base_score += (positive_count * 0.3) - (negative_count * 0.4)
        base_score += (commercial_pos * 0.4) - (commercial_neg * 0.3)
        
        # Look for explicit recommendations
        if any(phrase in text_lower for phrase in ['strong recommend', 'highly recommend']):
            base_score = max(base_score, 8.0)
        elif 'recommend' in text_lower and 'not' not in text_lower:
            base_score = max(base_score, 7.0)
        elif any(phrase in text_lower for phrase in ['pass', 'not recommend', 'avoid']):
            base_score = min(base_score, 4.0)
        
        # Add slight randomness based on text content
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        import random
        random.seed(text_hash % 2147483647)
        variation = (random.random() - 0.5) * 0.4  # ±0.2 variation
        base_score += variation
        
        # Ensure bounds
        return max(1.0, min(10.0, base_score))
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation for GPT models)"""
        return max(1, len(text) // 4)
    
    def to_database_format(self, result: OpenAIResult) -> Dict[str, Any]:
        """Convert OpenAI result to database format"""
        
        db_data = {
            'openai_score': result.score,
            'openai_recommendation': result.recommendation,
            'openai_verdict': result.verdict,
            'openai_confidence': result.confidence,
            'openai_raw_response': result.raw_response
        }
        
        # Add OpenAI-specific analysis data as JSON
        db_data['openai_commercial_assessment'] = json.dumps(result.commercial_assessment) if result.commercial_assessment else None
        db_data['openai_technical_craft'] = json.dumps(result.technical_craft) if result.technical_craft else None
        db_data['openai_industry_comparison'] = json.dumps(result.industry_comparison) if result.industry_comparison else None
        
        # Add Hollywood movie poster data
        db_data['openai_movie_poster_url'] = result.movie_poster_url
        db_data['openai_poster_prompt'] = result.poster_generation_prompt
        
        return db_data

    async def _generate_movie_poster(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Generate Hollywood movie poster using DALL-E 3 with advanced prompting"""
        
        try:
            # Extract rich analysis data for personalized poster creation
            score = analysis_data.get('score', 5.0)
            recommendation = analysis_data.get('recommendation', 'Consider')
            themes = analysis_data.get('themes', [])
            tone = analysis_data.get('tone', 'dramatic')
            characters = analysis_data.get('main_characters', [])
            
            # Advanced genre-specific styling with cinematic references
            genre_styles = {
                'horror': {
                    'visual': "dark atmospheric horror poster, deep shadows, blood-red accents, gothic typography, haunting silhouettes, supernatural elements, psychological tension, noir lighting",
                    'composition': "asymmetrical composition, negative space, ominous foreground elements",
                    'color': "desaturated palette with strategic red highlights, deep blacks, muted grays",
                    'reference': "inspired by The Conjuring, Hereditary, Get Out poster aesthetics"
                },
                'thriller': {
                    'visual': "suspenseful thriller poster, dramatic chiaroscuro lighting, urban noir aesthetic, tension-filled composition, mysterious shadows",
                    'composition': "diagonal compositions, fragmented imagery, overlapping elements",
                    'color': "high contrast black and white with selective color pops, steel blues, amber highlights",
                    'reference': "inspired by Seven, Gone Girl, Zodiac poster design"
                },
                'comedy': {
                    'visual': "vibrant comedy poster, bright saturated colors, playful typography, energetic character poses, whimsical elements",
                    'composition': "centered character focus, dynamic action poses, comedic visual gags",
                    'color': "warm sunny palette, bright yellows, cheerful blues, energetic oranges",
                    'reference': "inspired by The Grand Budapest Hotel, Superbad, Bridesmaids poster style"
                },
                'romantic comedy': {
                    'visual': "romantic comedy poster, soft romantic lighting, charming character chemistry, elegant script typography, heart-warming visual metaphors",
                    'composition': "romantic couple positioning, dreamy backgrounds, intimate framing",
                    'color': "warm romantic palette, soft pinks, golden hour lighting, pastel accents",
                    'reference': "inspired by The Proposal, Crazy Rich Asians, When Harry Met Sally poster aesthetics"
                },
                'action': {
                    'visual': "explosive action poster, dynamic motion blur, heroic character poses, dramatic lighting, high-energy composition, metallic textures",
                    'composition': "diagonal action lines, explosive backgrounds, heroic silhouettes",
                    'color': "bold primary colors, fiery oranges, electric blues, metallic silvers",
                    'reference': "inspired by Mad Max Fury Road, John Wick, Mission Impossible poster design"
                },
                'adventure': {
                    'visual': "epic adventure poster, sweeping landscapes, heroic journey imagery, golden hour lighting, majestic scale, exploration themes",
                    'composition': "epic wide shots, journey pathways, heroic character positioning",
                    'color': "epic golden palette, adventure blues, earth tones, sunset oranges",
                    'reference': "inspired by Indiana Jones, The Lord of the Rings, Pirates of the Caribbean poster style"
                },
                'drama': {
                    'visual': "emotional drama poster, intimate character portraits, subtle lighting, artistic composition, human connection themes, award-season aesthetic",
                    'composition': "character-focused framing, emotional close-ups, meaningful negative space",
                    'color': "sophisticated muted palette, warm golden tones, deep emotional blues",
                    'reference': "inspired by Moonlight, Manchester by the Sea, The Shape of Water poster design"
                },
                'sci-fi': {
                    'visual': "futuristic sci-fi poster, high-tech aesthetic, neon lighting, space elements, advanced technology, cyberpunk influences, holographic effects",
                    'composition': "futuristic architecture, technological interfaces, cosmic backgrounds",
                    'color': "cool futuristic palette, electric blues, neon greens, metallic silvers, deep space blacks",
                    'reference': "inspired by Blade Runner 2049, Arrival, Ex Machina poster aesthetics"
                },
                'fantasy': {
                    'visual': "epic fantasy poster, magical elements, mystical lighting, otherworldly creatures, enchanted landscapes, medieval influences",
                    'composition': "magical realms, mythical creatures, heroic fantasy positioning",
                    'color': "mystical palette, deep purples, magical golds, enchanted greens, ethereal blues",
                    'reference': "inspired by The Lord of the Rings, Game of Thrones, Pan's Labyrinth poster design"
                },
                'western': {
                    'visual': "classic western poster, dusty landscapes, dramatic silhouettes, vintage typography, frontier aesthetic, golden hour desert lighting",
                    'composition': "wide western vistas, lone figure silhouettes, frontier town elements",
                    'color': "desert palette, dusty browns, sunset oranges, weathered textures",
                    'reference': "inspired by The Good, The Bad and The Ugly, True Grit, Hell or High Water poster style"
                }
            }
            
            # Get genre-specific styling or default
            style_info = genre_styles.get(genre.lower(), {
                'visual': "professional Hollywood movie poster, cinematic composition, dramatic lighting, theatrical quality",
                'composition': "balanced composition, professional framing",
                'color': "cinematic color grading, professional palette",
                'reference': "inspired by classic Hollywood poster design"
            })
            
            # Quality and budget tier based on analysis score
            if score >= 9.0:
                quality_tier = "Oscar-caliber masterpiece"
                production_value = "A24 arthouse meets Marvel blockbuster production value"
            elif score >= 8.0:
                quality_tier = "award-winning blockbuster"
                production_value = "major studio theatrical release quality"
            elif score >= 7.0:
                quality_tier = "professional theatrical release"
                production_value = "mid-budget studio production value"
            elif score >= 6.0:
                quality_tier = "solid commercial release"
                production_value = "independent studio quality"
            else:
                quality_tier = "indie artistic vision"
                production_value = "festival circuit aesthetic"
            
            # Create advanced DALL-E 3 optimized prompt for Hollywood-quality results
            poster_prompt = f"""**HOLLYWOOD THEATRICAL MOVIE POSTER**

**FILM:** "{title}" - {quality_tier} {genre}

**VISUAL STYLE:** {style_info['visual']}
**COMPOSITION:** {style_info['composition']}  
**COLOR GRADING:** {style_info['color']}
**STYLE REFERENCE:** {style_info['reference']}

**CRITICAL REQUIREMENTS:**
- Movie poster aspect ratio (27x40 inches / 2:3 ratio)
- PERFECT title typography with "{title}" prominently displayed
- Professional movie poster layout and hierarchy
- {production_value} visual quality
- Theatrical distribution standard
- NO text artifacts or spelling errors
- Clean, readable title treatment

**DESIGN EXCELLENCE:**
- Studio-quality graphic design
- Dramatic cinematic lighting
- Professional color grading
- Award-winning poster composition
- Compelling visual storytelling
- Genre-appropriate atmosphere
- Marketing campaign quality

**OUTPUT:** Photorealistic, high-quality movie poster that could be used for actual theatrical release, with flawless title typography and professional Hollywood marketing standards."""
            
            # Generate poster image using DALL-E 3
            poster_url = await self._call_dalle_api(poster_prompt, title)
            
            return poster_url, poster_prompt
                    
        except Exception as e:
            logger.error(f"❌ Enhanced poster generation failed: {e}")
            return None, None

    async def _call_dalle_api(self, prompt: str, title: str) -> Optional[str]:
        """Call DALL-E 3 API to generate poster image"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.dalle_model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1792",  # Movie poster aspect ratio
                "quality": "hd",      # High quality for Hollywood posters
                "style": "vivid"      # More cinematic and dramatic
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.dalle_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('data') and len(result['data']) > 0:
                        image_url = result['data'][0]['url']
                        logger.info(f"🎨 DALL-E 3 poster generated successfully")
                        # Save image locally for reliable serving
                        saved_url = await self._save_poster_image(image_url, title)
                        return saved_url or image_url
                    else:
                        logger.error(f"❌ DALL-E 3 returned no image data")
                        return None
                else:
                    error_text = response.text
                    logger.error(f"❌ DALL-E 3 API error {response.status_code}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ DALL-E 3 API call failed: {e}")
            return None

    async def _save_poster_image(self, image_url: str, title: str) -> Optional[str]:
        """Download and save generated poster image locally under uploads/posters"""
        try:
            import os
            poster_dir = "uploads/posters"
            os.makedirs(poster_dir, exist_ok=True)
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            filename = f"openai_{safe_title}_{int(time.time())}.png"
            filepath = os.path.join(poster_dir, filename)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        relative_url = f"/uploads/posters/{filename}"
                        logger.info(f"✅ OpenAI poster saved: {relative_url} ({os.path.getsize(filepath)} bytes)")
                        return relative_url
        except Exception as e:
            logger.warning(f"⚠️  Failed to save OpenAI poster locally: {e}")
        return None
