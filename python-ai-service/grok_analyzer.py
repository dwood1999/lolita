#!/usr/bin/env python3
"""
Grok 4 Screenplay Analyzer
Provides secondary AI evaluation alongside Claude Opus 4.1
"""

import os
import json
import time
import logging
import base64
import uuid
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
class GrokResult:
    """Grok 4 analysis result with enhanced cultural and market insights"""
    score: float  # 0-10
    recommendation: str  # "Pass", "Consider", "Recommend", "Strong Recommend"
    verdict: str  # One-line assessment
    processing_time: float
    cost: float
    confidence: float
    raw_response: str
    
    # Phase 1 Enhancements
    cultural_reality_check: Optional[Dict[str, Any]] = None
    brutal_honesty_assessment: Optional[Dict[str, Any]] = None
    controversy_analysis: Optional[Dict[str, Any]] = None
    
    # Phase 2 Enhancement - Hollywood Movie Poster
    movie_poster_url: Optional[str] = None
    poster_generation_prompt: Optional[str] = None

class GrokAnalyzer:
    """Grok 4 API integration for screenplay analysis with enhanced cultural insights"""
    
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-4-latest"
        
        # Pricing (estimated - adjust based on actual Grok pricing)
        self.input_cost_per_token = 0.00001  # $0.01 per 1K tokens
        self.output_cost_per_token = 0.00003  # $0.03 per 1K tokens
        
        # Phase 1 Enhancement Modules
        self.cultural_analysis_enabled = True
        self.brutal_honesty_enabled = True
        self.controversy_scanner_enabled = True
        
        # Phase 2 Enhancement - Movie Poster Generation
        self.poster_generation_enabled = False  # Disabled - using OpenAI GPT-5 instead
        # Movie poster generation moved to OpenAI GPT-5 for better quality
        
        if not self.api_key:
            logger.warning("⚠️  XAI_API_KEY not set - Grok analysis will be disabled")
        else:
            logger.info("🤖 Grok 4 Analyzer initialized with Phase 1 enhancements")
    
    async def analyze(self, screenplay_text: str, title: str, genre: str = "", budget_estimate: Optional[float] = None) -> Optional[GrokResult]:
        """Analyze screenplay with Grok 4"""
        
        if not self.api_key:
            logger.warning("❌ Grok analysis skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create focused prompt for Grok
            prompt = self._create_prompt(screenplay_text, title, genre, budget_estimate)
            
            # Call Grok API
            response = await self._call_grok_api(prompt)
            
            # Parse response
            analysis_data = self._parse_response(response)
            
            # Calculate cost
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
            
            processing_time = time.time() - start_time
            
            # Generate Hollywood movie poster if enabled
            poster_url = None
            poster_prompt = None
            if self.poster_generation_enabled and self.api_key:
                try:
                    poster_url, poster_prompt = await self._generate_movie_poster_with_grok(title, genre, analysis_data)
                    logger.info(f"🎬 Movie poster generated successfully with Grok 4")
                except Exception as e:
                    logger.warning(f"⚠️  Poster generation failed: {e}")
            
            result = GrokResult(
                score=analysis_data.get('score', 0.0),
                recommendation=analysis_data.get('recommendation', 'Pass'),
                verdict=analysis_data.get('verdict', 'Analysis incomplete'),
                processing_time=processing_time,
                cost=cost,
                confidence=analysis_data.get('confidence', 0.5),
                raw_response=response,
                cultural_reality_check=analysis_data.get('cultural_reality_check'),
                brutal_honesty_assessment=analysis_data.get('brutal_honesty_assessment'),
                controversy_analysis=analysis_data.get('controversy_analysis'),
                movie_poster_url=poster_url,
                poster_generation_prompt=poster_prompt
            )
            
            logger.info(f"🤖 Grok analysis completed in {processing_time:.2f}s")
            logger.info(f"💰 Grok cost: ${cost:.4f}")
            logger.info(f"⭐ Grok score: {result.score}/10 ({result.recommendation})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Grok analysis failed: {type(e).__name__}: {str(e)}")
            logger.error(f"❌ Grok error details: {repr(e)}")
            import traceback
            logger.error(f"❌ Grok traceback: {traceback.format_exc()}")
            return None
    
    def _create_prompt(self, screenplay_text: str, title: str, genre: str, budget_estimate: Optional[float] = None) -> str:
        """Create enhanced prompt for Grok 4 with Phase 1 cultural analysis"""
        
        # Truncate if too long (Grok has context limits)
        max_chars = 50000  # Adjust based on Grok's limits
        if len(screenplay_text) > max_chars:
            screenplay_text = screenplay_text[:max_chars] + "\n\n[TRUNCATED FOR ANALYSIS]"
        
        # Enhanced budget context with AI estimation and Grok's brutal honesty
        estimated_budget = None
        if not budget_estimate:
            estimated_budget = estimate_budget_from_screenplay(screenplay_text, title, genre or "Drama")
        
        # Get budget context but add Grok's brutal spin
        budget_context = format_budget_context_for_ai(budget_estimate, estimated_budget)
        budget_for_casting = budget_estimate or estimated_budget[1] if estimated_budget else 10_000_000
        casting_strategy = get_casting_suggestions_by_budget(budget_for_casting, genre or "Drama")
        
        # Grok's brutal budget roast
        if budget_estimate:
            if budget_estimate < 100_000:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - This better be a single-location masterpiece or you're delusional about production costs."
            elif budget_estimate < 1_000_000:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - Mumblecore territory. Better hope your dialogue doesn't suck."
            elif budget_estimate < 5_000_000:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - Indie film territory. Can't hide weak writing with explosions."
            elif budget_estimate < 20_000_000:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - Mid-budget means no excuses for mediocrity."
            elif budget_estimate < 100_000_000:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - Studio money means studio expectations. Better not waste it."
            else:
                budget_roast = f"**BUDGET REALITY CHECK: ${budget_estimate:,.0f}** - Tentpole pressure. This better change cinema or you just burned a fortune."
        else:
            budget_roast = "**BUDGET REALITY CHECK: TBD** - Smart move not committing. I'll roast based on your story's delusions of grandeur."

        return f"""You are a brutally honest screenplay analyst with deep internet culture knowledge and 20+ years of industry experience. You're like a film studies major with a Twitter addiction who gives zero diplomatic cushioning. Your job is to roast this screenplay and give unfiltered, internet-native feedback that other AI won't provide.

**SCREENPLAY: "{title}"**
{f"**GENRE: {genre}**" if genre else ""}
{budget_roast}

**SCREENPLAY TEXT:**
{screenplay_text}

**NUCLEAR ANALYSIS PROTOCOL - NO MERCY MODE:**

## **PHASE 1: CULTURAL REALITY CHECK** 🎭
Give me the unfiltered truth about what would get absolutely roasted on Film Twitter:

1. **Cringe Detection**: Rate each character's dialogue for cringe factor on a 1-10 scale where 10 is "this would become a viral meme for all the wrong reasons"
2. **Meme Potential**: What parts of this script would get absolutely roasted on Film Twitter and why? Which scenes have "hello fellow kids" energy that would get screenshot and mocked?
3. **Discourse Prediction**: What would be the most controversial hot takes about this screenplay on social media? What would be the top 3 criticisms in the quote-tweets if this got made?
4. **Zeitgeist Alignment**: What outdated tropes or references would make audiences roll their eyes and tweet "OK boomer"?

## **PHASE 2: DEMOGRAPHIC AUTHENTICITY AUDIT** 🔍
Strip away the writer's ego - brutal authenticity check:

1. **Gen Z vs Millennial Writing**: Does the Gen Z dialogue actually sound like how people talk, or does it sound like a millennial writer trying too hard?
2. **Subculture Authenticity**: Rate the authenticity of any specific subculture representation - would actual members of this group cringe?
3. **Social Media Realism**: Are the social media/texting scenes realistic or do they scream "written by someone who doesn't use the internet"?
4. **Demographic Reality**: If someone from [specific demographic/subculture] read this, would they think the writer actually knows their world or would they cringe at how off-base it is?

## **PHASE 3: BRUTAL HONESTY MODE** 💀
No sugar-coating - what would actual humans say behind closed doors:

1. **Protagonist Reality Check**: Strip away writer's ego - what would actual humans say about this protagonist behind closed doors? Would audiences actually root for them or find them insufferable?
2. **TikTok-Brain Pacing**: Does this hold TikTok-brain attention or drag? Where would people check their phones?
3. **Competition Brutality**: Brutal comparison - how does this stack against similar successful films? Be specific about what's been done better.
4. **Production Reality**: Budget vs reality check - is this actually shootable or is it delusional?

## **PHASE 4: DISCOURSE PREDICTION ENGINE** 🔮
Predict the exact internet drama this would cause:

1. **Think-Piece Generator**: Write the angry video essay title this would inspire and the counter-response video essay title that would follow
2. **Twitter Drama Assessment**: What elements would cause Twitter drama, and is that good or bad for the project?
3. **Quote-Tweet Predictions**: Predict the exact type of think-pieces this would spawn - give me the headline formats
4. **Viral Moment Scanner**: What scenes would become viral TikToks (good or bad)?

## **PHASE 5: GENRE FRESHNESS ASSESSMENT** 🎬
On a scale of "innovative" to "meme-tier predictable":

1. **Innovation Scale**: On a scale of 'innovative' to 'meme-tier predictable,' where does this {genre} land?
2. **Twitter Joke Fodder**: What genre conventions am I leaning on that have become Twitter joke fodder?
3. **Self-Awareness Check**: Should this script lean into being self-aware about its tropes or would that feel forced?
4. **Freshness Reality**: What's been done to death in this genre that this script is still doing?

## **PHASE 6: MARKET POSITIONING INTELLIGENCE** 📊
Brutal market reality check:

1. **Platform Fit**: Streaming vs theatrical - where does this actually belong and why?
2. **Target Demo Reality**: Who actually watches this vs who the writer thinks will watch this?
3. **Oscar Bait Detection**: Does this feel calculated vs organic? Is it trying too hard to be "important"?
4. **Comp Title Brutality**: Brutal comparison to similar films - what did they do that this doesn't?

**RESPONSE FORMAT:**
Provide analysis as JSON with these exact keys:
{{
    "score": 0.0,
    "recommendation": "",
    "verdict": "",
    "confidence": 0.0,
    "cultural_reality_check": {{
        "cringe_factor": 0,
        "meme_potential": "",
        "twitter_discourse": "",
        "zeitgeist_score": 0,
        "hello_fellow_kids_energy": ""
    }},
    "demographic_authenticity_audit": {{
        "gen_z_dialogue_authenticity": "",
        "subculture_authenticity_rating": "",
        "social_media_realism": "",
        "demographic_accuracy": ""
    }},
    "brutal_honesty_assessment": {{
        "protagonist_reality_check": "",
        "tiktok_brain_pacing": "",
        "competition_brutality": "",
        "production_reality": ""
    }},
    "discourse_prediction_engine": {{
        "think_piece_titles": [],
        "twitter_drama_assessment": "",
        "quote_tweet_predictions": [],
        "viral_moment_scanner": ""
    }},
    "genre_freshness_assessment": {{
        "innovation_scale": "",
        "twitter_joke_fodder": "",
        "self_awareness_check": "",
        "freshness_reality": ""
    }},
    "market_positioning_intelligence": {{
        "platform_fit": "",
        "target_demo_reality": "",
        "oscar_bait_detection": "",
        "comp_title_brutality": ""
    }}
}}

**SCORING GUIDE:**
- 9-10: Exceptional, internet would stan this
- 7-8: Strong, minor tweaks needed
- 5-6: Promising but needs major work
- 3-4: Weak, would get roasted online
- 0-2: Not viable, meme-tier bad

**TONE:** Be direct, internet-savvy, and brutally honest. Use current cultural references. Don't sugarcoat - give the unfiltered truth that helps writers improve."""

    async def _call_grok_api(self, prompt: str) -> str:
        """Call Grok API with error handling"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a brutally honest screenplay analyst who's like a film studies major with a Twitter addiction. You give zero diplomatic cushioning and provide unfiltered, internet-native feedback that other AI won't give. You understand current cultural discourse, meme culture, and what gets roasted on Film Twitter. Your job is to roast screenplays and give the hard truths that help writers improve."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_completion_tokens": 3000,  # Increased for enhanced analysis with all categories
            "temperature": 0.7,   # Higher temperature for more creative/brutal responses
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=90.0) as client:  # Increased timeout
            try:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
            except httpx.ReadTimeout:
                logger.error("❌ Grok API timeout after 90 seconds")
                raise Exception("Grok API timeout - service may be overloaded")
            except httpx.ConnectTimeout:
                logger.error("❌ Grok API connection timeout")
                raise Exception("Grok API connection timeout")
            except Exception as e:
                logger.error(f"❌ Grok API request failed: {e}")
                raise
            
            if response.status_code != 200:
                raise Exception(f"Grok API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                raise Exception("Invalid Grok API response format")
            
            return data['choices'][0]['message']['content']
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse enhanced Grok response into structured data"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            
            if json_match:
                json_str = json_match.group()
                
                # Try to fix truncated JSON by adding missing closing braces
                json_str = self._fix_truncated_json(json_str)
                
                parsed_data = json.loads(json_str)
                
                # Validate and structure the enhanced response
                return self._validate_enhanced_response(parsed_data)
            else:
                # Fallback parsing if no JSON found
                logger.warning("⚠️  No JSON found in Grok response, using fallback parsing")
                return self._fallback_parse(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON parsing failed: {e}, attempting to fix truncated JSON")
            # Try to fix truncated JSON and parse again
            try:
                json_match = re.search(r'\{[\s\S]*', response)  # Match even incomplete JSON
                if json_match:
                    json_str = self._fix_truncated_json(json_match.group())
                    parsed_data = json.loads(json_str)
                    logger.info("✅ Successfully parsed truncated JSON after repair")
                    return self._validate_enhanced_response(parsed_data)
            except:
                pass
            
            logger.warning("⚠️  All JSON parsing attempts failed, using fallback")
            return self._fallback_parse(response)
    
    def _fix_truncated_json(self, json_str: str) -> str:
        """Attempt to fix truncated JSON by adding missing closing braces and quotes"""
        
        # Count opening and closing braces/brackets
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # If JSON is truncated in the middle of a string value, close the string
        if json_str.count('"') % 2 == 1:
            # Odd number of quotes means we're in the middle of a string
            json_str += '"'
        
        # Add missing closing brackets
        while close_brackets < open_brackets:
            json_str += ']'
            close_brackets += 1
        
        # Add missing closing braces
        while close_braces < open_braces:
            json_str += '}'
            close_braces += 1
        
        return json_str
    
    def _validate_enhanced_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure the enhanced Grok response"""
        
        # Ensure basic fields exist
        validated = {
            'score': data.get('score', 5.0),
            'recommendation': data.get('recommendation', 'Consider'),
            'verdict': data.get('verdict', 'Analysis completed'),
            'confidence': data.get('confidence', 0.7)
        }
        
        # Validate Enhanced Analysis Categories
        if 'cultural_reality_check' in data:
            cultural = data['cultural_reality_check']
            validated['cultural_reality_check'] = {
                'cringe_factor': min(10, max(1, cultural.get('cringe_factor', 5))),
                'meme_potential': cultural.get('meme_potential', 'Low meme potential'),
                'twitter_discourse': cultural.get('twitter_discourse', 'Neutral reception expected'),
                'zeitgeist_score': min(10, max(1, cultural.get('zeitgeist_score', 5))),
                'hello_fellow_kids_energy': cultural.get('hello_fellow_kids_energy', 'No obvious pandering detected')
            }
        
        if 'demographic_authenticity_audit' in data:
            demo = data['demographic_authenticity_audit']
            validated['demographic_authenticity_audit'] = {
                'gen_z_dialogue_authenticity': demo.get('gen_z_dialogue_authenticity', 'Authenticity unclear'),
                'subculture_authenticity_rating': demo.get('subculture_authenticity_rating', 'No specific subcultures identified'),
                'social_media_realism': demo.get('social_media_realism', 'Social media usage not prominent'),
                'demographic_accuracy': demo.get('demographic_accuracy', 'General demographic representation')
            }
        
        if 'brutal_honesty_assessment' in data:
            brutal = data['brutal_honesty_assessment']
            validated['brutal_honesty_assessment'] = {
                'protagonist_reality_check': brutal.get('protagonist_reality_check', 'Protagonist assessment unclear'),
                'tiktok_brain_pacing': brutal.get('tiktok_brain_pacing', 'Pacing analysis needed'),
                'competition_brutality': brutal.get('competition_brutality', 'Competitive analysis needed'),
                'production_reality': brutal.get('production_reality', 'Production feasibility unclear')
            }
        
        if 'discourse_prediction_engine' in data:
            discourse = data['discourse_prediction_engine']
            validated['discourse_prediction_engine'] = {
                'think_piece_titles': discourse.get('think_piece_titles', []),
                'twitter_drama_assessment': discourse.get('twitter_drama_assessment', 'Low drama potential'),
                'quote_tweet_predictions': discourse.get('quote_tweet_predictions', []),
                'viral_moment_scanner': discourse.get('viral_moment_scanner', 'No obvious viral moments')
            }
        
        if 'genre_freshness_assessment' in data:
            genre_fresh = data['genre_freshness_assessment']
            validated['genre_freshness_assessment'] = {
                'innovation_scale': genre_fresh.get('innovation_scale', 'Standard genre execution'),
                'twitter_joke_fodder': genre_fresh.get('twitter_joke_fodder', 'No obvious joke fodder'),
                'self_awareness_check': genre_fresh.get('self_awareness_check', 'Self-awareness level unclear'),
                'freshness_reality': genre_fresh.get('freshness_reality', 'Freshness assessment needed')
            }
        
        if 'market_positioning_intelligence' in data:
            market = data['market_positioning_intelligence']
            validated['market_positioning_intelligence'] = {
                'platform_fit': market.get('platform_fit', 'Platform fit unclear'),
                'target_demo_reality': market.get('target_demo_reality', 'Target demographic unclear'),
                'oscar_bait_detection': market.get('oscar_bait_detection', 'Oscar potential unclear'),
                'comp_title_brutality': market.get('comp_title_brutality', 'Comparable titles analysis needed')
            }
        
        # Legacy support for old controversy_analysis field
        if 'controversy_analysis' in data:
            controversy = data['controversy_analysis']
            validated['controversy_analysis'] = {
                'representation_risk': controversy.get('representation_risk', 'Low risk'),
                'backlash_potential': controversy.get('backlash_potential', 'Minimal backlash expected'),
                'polarization_level': controversy.get('polarization_level', 'Low polarization'),
                'boundary_assessment': controversy.get('boundary_assessment', 'Within acceptable boundaries')
            }
        
        return validated
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        
        # Extract score using regex
        import re
        
        score_match = re.search(r'score["\s:]*(\d+\.?\d*)', response, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else 5.0
        
        # Determine recommendation based on score
        if score >= 8.5:
            recommendation = "Strong Recommend"
        elif score >= 7.0:
            recommendation = "Recommend"
        elif score >= 5.0:
            recommendation = "Consider"
        else:
            recommendation = "Pass"
        
        # Extract verdict (first sentence or paragraph)
        lines = response.split('\n')
        verdict = next((line.strip() for line in lines if len(line.strip()) > 20), "Analysis completed")
        
        return {
            'score': score,
            'recommendation': recommendation,
            'verdict': verdict[:200],  # Limit length
            'confidence': 0.7  # Default confidence
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return max(1, len(text) // 4)
    
    async def _generate_movie_poster_with_grok(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Generate Hollywood movie poster using image generation API"""
        
        try:
            # Create a concise, visual prompt for image generation
            score = analysis_data.get('score', 5.0)
            recommendation = analysis_data.get('recommendation', 'Consider')
            
            # Determine poster style based on genre and score
            if genre.lower() in ['horror', 'thriller']:
                style = "dark atmospheric thriller movie poster, dramatic shadows, suspenseful lighting, noir style"
            elif genre.lower() in ['comedy', 'romantic comedy']:
                style = "bright colorful comedy movie poster, vibrant colors, fun uplifting mood, playful design"
            elif genre.lower() in ['action', 'adventure']:
                style = "dynamic action movie poster, explosive energy, bold composition, cinematic drama"
            elif genre.lower() in ['drama']:
                style = "emotional drama movie poster, warm lighting, character-focused, artistic depth"
            elif genre.lower() in ['sci-fi', 'science fiction']:
                style = "futuristic sci-fi movie poster, high-tech aesthetic, cool blue tones, space elements"
            else:
                style = "professional Hollywood movie poster, cinematic composition, dramatic lighting"
            
            # Quality modifier based on Grok score
            if score >= 8.0:
                quality = "award-winning blockbuster"
            elif score >= 6.0:
                quality = "professional theatrical"
            else:
                quality = "indie artistic"
                
            # Create image generation prompt (optimized for DALL-E/Midjourney style)
            image_prompt = f"""Movie poster for "{title}", {quality} {style}, professional movie poster design, theatrical one-sheet, dramatic composition, high quality digital art, movie title typography, {genre} genre, cinematic lighting, poster art style"""
            
            # Try to generate actual image using OpenAI DALL-E
            poster_url = await self._generate_poster_image(image_prompt, title)
            
            return poster_url, image_prompt
                    
        except Exception as e:
            logger.error(f"❌ Poster generation failed: {e}")
            return None, None

    async def _generate_poster_image(self, prompt: str, title: str) -> Optional[str]:
        """Generate actual poster image using OpenAI DALL-E"""
        
        # Check if OpenAI API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.warning("⚠️  OPENAI_API_KEY not set - using placeholder poster")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1792",  # Movie poster aspect ratio
                "quality": "standard",
                "style": "vivid"
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and len(data['data']) > 0:
                        image_url = data['data'][0]['url']
                        logger.info(f"🎬 Generated poster image for '{title}'")
                        
                        # Save image locally (optional)
                        saved_url = await self._save_poster_image(image_url, title)
                        return saved_url or image_url
                    else:
                        logger.error("No image data in DALL-E response")
                        return None
                else:
                    logger.error(f"DALL-E API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return None

    async def _save_poster_image(self, image_url: str, title: str) -> Optional[str]:
        """Save generated poster image locally"""
        
        try:
            # Create uploads directory if it doesn't exist
            poster_dir = "uploads/posters"
            os.makedirs(poster_dir, exist_ok=True)
            
            # Generate filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{int(time.time())}.png"
            filepath = os.path.join(poster_dir, filename)
            
            logger.info(f"🔄 Downloading poster from: {image_url}")
            logger.info(f"💾 Saving to: {filepath}")
            
            # Download and save image
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify file was saved and return proper URL
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        relative_url = f"/uploads/posters/{filename}"
                        logger.info(f"✅ Poster saved: {relative_url} ({os.path.getsize(filepath)} bytes)")
                        return relative_url
                    else:
                        logger.error(f"❌ File not saved or empty: {filepath}")
                        return None
                else:
                    logger.error(f"❌ Failed to download image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to save poster image: {e}")
            return None

    def to_database_format(self, result: GrokResult) -> Dict[str, Any]:
        """Convert enhanced Grok result to database format"""
        
        db_data = {
            'grok_score': result.score,
            'grok_recommendation': result.recommendation,
            'grok_verdict': result.verdict,
            'grok_confidence': result.confidence,
            'grok_raw_response': result.raw_response
        }
        
        # Add enhanced analysis data as JSON - combine all categories into cultural_analysis for storage
        enhanced_analysis = {}
        if result.cultural_reality_check:
            enhanced_analysis['cultural_reality_check'] = result.cultural_reality_check
        if result.brutal_honesty_assessment:
            enhanced_analysis['brutal_honesty_assessment'] = result.brutal_honesty_assessment
        if result.controversy_analysis:
            enhanced_analysis['controversy_analysis'] = result.controversy_analysis
            
        # Store all enhanced analysis in the cultural_analysis field for now (backward compatibility)
        db_data['grok_cultural_analysis'] = json.dumps(enhanced_analysis) if enhanced_analysis else None
        db_data['grok_brutal_honesty'] = json.dumps(result.brutal_honesty_assessment) if result.brutal_honesty_assessment else None
        db_data['grok_controversy_analysis'] = json.dumps(result.controversy_analysis) if result.controversy_analysis else None
        
        # Add Phase 2 enhancement - Movie Poster
        db_data['grok_movie_poster_url'] = result.movie_poster_url
        db_data['grok_poster_prompt'] = result.poster_generation_prompt
        
        return db_data
