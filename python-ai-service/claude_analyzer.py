"""
Claude Opus 4.1 Screenplay Analyzer
Superior narrative understanding with advanced AI capabilities
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from budget_utils import format_budget_context_for_ai, estimate_budget_from_screenplay, get_casting_suggestions_by_budget

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Structured analysis result from Claude"""
    id: str
    title: str
    genre: str
    detected_genre: Optional[str]
    subgenre: Optional[str]
    
    # Core Analysis
    overall_score: float  # 0-10
    recommendation: str  # "Pass", "Consider", "Recommend", "Strong Recommend"
    
    # Executive Summary
    one_line_verdict: str
    logline: str
    executive_summary: str
    
    # Strengths & Weaknesses
    top_strengths: List[str]
    key_weaknesses: List[str]
    suggestions: List[str]
    
    # Market Perspective
    commercial_viability: str
    target_audience: str
    comparable_films: List[str]
    
    # Casting Suggestions
    casting_suggestions: List[Dict[str, Any]]
    
    # Director Recommendation
    director_recommendation: str
    
    # Technical Details
    processing_time: float
    ai_model: str
    confidence_level: float  # 0-1
    cost: float
    
    # Metadata
    timestamp: datetime
    raw_api_request: Optional[str] = None
    raw_api_response: Optional[str] = None

class ClaudeOpusAnalyzer:
    """
    Claude Opus 4.1 Analyzer with superior capabilities:
    - Superior narrative understanding - catches subtle themes, subtext, foreshadowing
    - Better character psychology - deeper analysis of motivations and arcs
    - Nuanced tone detection - understands irony, satire, dark comedy better
    - Complex structural analysis - recognizes non-linear narratives, parallel storylines
    - Richer creative suggestions - more innovative solutions to script problems
    """
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = 'claude-opus-4-1-20250805'  # Claude Opus 4.1
        
        # Pricing (per 1M tokens) - Claude Opus 4.1
        self.input_cost_per_token = 15.0 / 1_000_000  # $15 per 1M input tokens
        self.output_cost_per_token = 75.0 / 1_000_000  # $75 per 1M output tokens
        
        logger.info("🎯 Claude Opus 4.1 Analyzer initialized (claude-opus-4-1-20250805)")
    
    async def analyze_screenplay(
        self,
        screenplay_text: str,
        title: str,
        genre: Optional[str] = None,
        user_id: Optional[str] = None,
        budget_estimate: Optional[float] = None
    ) -> AnalysisResult:
        """Perform comprehensive screenplay analysis using Claude Opus 4.1"""
        
        start_time = time.time()
        analysis_id = f"claude_analysis_{int(time.time() * 1000)}_{title.replace(' ', '_')}"
        
        logger.info(f"🎬 Starting Claude Opus 4.1 analysis for: {title}")
        logger.info(f"📄 Text length: {len(screenplay_text):,} characters")
        
        try:
            # Determine if we need genre detection
            needs_genre_detection = not genre or genre.strip() == ''
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(screenplay_text, title, genre, needs_genre_detection, budget_estimate)
            
            # Call Claude API
            logger.info("🔄 Sending request to Claude Opus 4.1...")
            response = await self._call_claude_api(prompt)
            
            # Parse the response
            analysis_data = self._parse_response(response)
            
            # Calculate cost
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
            
            processing_time = time.time() - start_time
            
            # Create result object
            result = AnalysisResult(
                id=analysis_id,
                title=title,
                genre=genre or analysis_data.get('detected_genre', 'Drama'),
                detected_genre=analysis_data.get('detected_genre') if needs_genre_detection else None,
                subgenre=analysis_data.get('subgenre'),
                overall_score=analysis_data.get('overall_score', 0),
                recommendation=analysis_data.get('recommendation', 'Pass'),
                one_line_verdict=analysis_data.get('one_line_verdict', 'Analysis incomplete'),
                logline=analysis_data.get('logline', 'Logline not available'),
                executive_summary=analysis_data.get('executive_summary', 'Summary not available'),
                top_strengths=analysis_data.get('top_strengths', []),
                key_weaknesses=analysis_data.get('key_weaknesses', []),
                suggestions=analysis_data.get('suggestions', []),
                commercial_viability=analysis_data.get('commercial_viability', 'Unknown'),
                target_audience=analysis_data.get('target_audience', 'General'),
                comparable_films=analysis_data.get('comparable_films', []),
                casting_suggestions=analysis_data.get('casting_suggestions', []),
                director_recommendation=analysis_data.get('director_recommendation', 'Director recommendation not available'),
                processing_time=processing_time,
                ai_model='Claude Opus 4.1',
                confidence_level=analysis_data.get('confidence', 0.5),
                cost=cost,
                timestamp=datetime.now(),
                raw_api_request=prompt,
                raw_api_response=response
            )
            
            logger.info(f"✅ Analysis completed in {processing_time:.2f}s")
            logger.info(f"💰 Cost: ${cost:.4f}")
            logger.info(f"⭐ Score: {result.overall_score}/10 ({result.recommendation})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Claude analysis failed: {e}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _create_analysis_prompt(
        self, 
        screenplay_text: str, 
        title: str, 
        genre: Optional[str], 
        detect_genre: bool,
        budget_estimate: Optional[float] = None
    ) -> str:
        """Create the comprehensive analysis prompt for Claude"""
        
        genre_instruction = ""
        if detect_genre:
            genre_instruction = """
IMPORTANT: The genre has not been specified. Based on the screenplay content, determine the primary genre.
Include "detected_genre" in your response with one of these genres:
Drama, Comedy, Thriller, Horror, Action, Romance, Sci-Fi, Fantasy, Mystery, Crime, Documentary, or Other.
"""
        
        # Enhanced budget context with AI estimation if needed
        estimated_budget = None
        if not budget_estimate:
            # Estimate budget from screenplay content
            estimated_budget = estimate_budget_from_screenplay(screenplay_text, title, genre or "Drama")
        
        budget_context = format_budget_context_for_ai(budget_estimate, estimated_budget)
        
        # Get budget-appropriate casting suggestions
        budget_for_casting = budget_estimate or estimated_budget[1] if estimated_budget else 10_000_000
        casting_strategy = get_casting_suggestions_by_budget(budget_for_casting, genre or "Drama")

        return f"""You are an elite screenplay analyst with deep expertise in story structure, character psychology, and cinematic storytelling. Provide a comprehensive professional analysis using advanced evaluation techniques.

SCREENPLAY ANALYSIS PROTOCOL:

**CORE ANALYTICAL FRAMEWORK:**
• Story Structure & Pacing: Analyze three-act structure, emotional beats, tension curves, momentum flow
• Character Development: Evaluate character arcs (want vs. need), dialogue authenticity, internal conflicts
• Thematic Analysis: Identify underlying themes, subtext depth, visual metaphors, symbolic elements
• Technical Craft: Assess scene efficiency, visual storytelling, filmable vs. novelistic writing
• Genre Mastery: Evaluate genre expectations fulfillment while avoiding clichés

Analyze this {f'{genre} ' if genre else ''}screenplay titled "{title}".
{genre_instruction}
{budget_context}

SCREENPLAY TEXT:
{screenplay_text}

**ANALYSIS REQUIREMENTS:**

**1. STRUCTURAL ASSESSMENT:**
- Map the inciting incident, plot points, and climax positioning
- Analyze pacing rhythm and identify where momentum lags or rushes
- Evaluate emotional beats and tension curve effectiveness
- Score theme integration without heavy-handedness

**2. CHARACTER EVALUATION:**
- Assess each major character's arc completion and motivation clarity
- Analyze dialogue distinction - does each character have a unique voice?
- Identify characters serving only plot functions vs. feeling authentic
- Map relationship dynamics and internal/external conflicts

**3. CRAFT ANALYSIS:**
- Evaluate scene descriptions for visual storytelling effectiveness
- Analyze transitions and narrative flow maintenance
- Assess subtext depth in key scenes
- Review opening pages for immediate stakes establishment

**4. GENRE & MARKET PERSPECTIVE:**
- Identify primary genre and specific subgenre (e.g., "Thriller" → "Psychological Thriller")
- Analyze genre convention adherence and intelligent subversions
- Evaluate from reader's perspective - where might attention wane?
- Assess logline strength and hook effectiveness
- Identify opportunities to deepen genre elements

Provide specific page references, concrete examples, and actionable revision strategies.

**RESPONSE STRUCTURE:**

1. OVERALL SCORE (0-10): Reflecting quality, craft, and commercial potential
2. RECOMMENDATION: "Pass", "Consider", "Recommend", "Strong Recommend"
3. ONE-LINE VERDICT: Captures essence and potential in one compelling sentence
4. LOGLINE: Professional, compelling one-sentence story summary (25-35 words)
5. EXECUTIVE SUMMARY: Comprehensive story, theme, and execution overview
6. STRUCTURAL ANALYSIS: Three-act breakdown, pacing assessment, plot point effectiveness
7. CHARACTER ANALYSIS: Arc evaluation, dialogue assessment, authenticity scoring
8. THEMATIC DEPTH: Theme identification, subtext analysis, symbolic element usage
9. CRAFT EVALUATION: Scene efficiency, visual storytelling, technical execution
10. GENRE MASTERY: Convention handling, cliché avoidance, innovation opportunities
11. TOP STRENGTHS: 4-6 specific, detailed strengths with examples
12. KEY WEAKNESSES: 4-6 constructive weaknesses with page references
13. IMPROVEMENT STRATEGIES: 5-7 prioritized, actionable revision suggestions
14. COMMERCIAL VIABILITY: Market potential, positioning, demographic analysis
15. TARGET AUDIENCE: Specific segments with connection reasoning
16. COMPARABLE FILMS: 4-6 similar successful films with strategic positioning
17. CASTING VISION: Major characters with 2-3 ideal actors and reasoning
   **BUDGET-APPROPRIATE CASTING FRAMEWORK:**
   - Lead Strategy: {casting_strategy['lead_strategy']}
   - Supporting Strategy: {casting_strategy['supporting_strategy']}
   - Star Power Level: {casting_strategy['star_power']}
   - Budget Allocation: {casting_strategy['budget_allocation']}
   - Genre Considerations: {casting_strategy['genre_considerations']}
   
   Use this framework to provide realistic, achievable casting suggestions within the specified budget constraints.

18. DIRECTOR RECOMMENDATION: 2-3 directors whose style/vision would best serve this material within the budget range, with specific reasoning

Focus on psychological depth, structural sophistication, and actionable insights that elevate the screenplay's potential.

Format your response as a JSON object with these exact keys:
{{
    "overall_score": 0.0,
    "recommendation": "",
    "one_line_verdict": "",
    "logline": "",
    "executive_summary": "",
    "structural_analysis": "",
    "character_analysis": "",
    "thematic_depth": "",
    "craft_evaluation": "",
    "genre_mastery": "",
    "top_strengths": [],
    "key_weaknesses": [],
    "improvement_strategies": [],
    "commercial_viability": "",
    "target_audience": "",
    "comparable_films": [],
    "casting_vision": [{{"character": "", "actors": [], "reasoning": ""}}],
    "director_recommendation": "",
    "subgenre": "",
    "confidence": 0.0{',\n    "detected_genre": ""' if detect_genre else ''}
}}

Be specific, insightful, and constructive. Provide analysis that demonstrates deep understanding of storytelling craft and industry standards."""

    async def _call_claude_api(self, prompt: str) -> str:
        """Call Claude API with error handling and retry logic for overloaded servers"""
        import asyncio
        
        # Retry delays: 5, 10, 20, 30, 40, 50, 60 seconds
        retry_delays = [5, 10, 20, 30, 40, 50, 60]
        
        for attempt in range(len(retry_delays) + 1):  # +1 for initial attempt
            try:
                # Try the new messages API first
                if hasattr(self.client, 'messages'):
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=4000,
                        temperature=0.3,  # Lower temperature for more consistent analysis
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    return response.content[0].text if response.content else ""
                
                # Fallback to older API
                elif hasattr(self.client, 'completions'):
                    response = self.client.completions.create(
                        model=self.model,
                        prompt=f"Human: {prompt}\n\nAssistant:",
                        max_tokens_to_sample=4000,
                        temperature=0.3
                    )
                    return response.completion
                
                # Try direct completion method
                else:
                    response = self.client.completion(
                        model=self.model,
                        prompt=f"Human: {prompt}\n\nAssistant:",
                        max_tokens_to_sample=4000,
                        temperature=0.3
                    )
                    return response.get('completion', '')
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an overloaded error (529) - only retry for this
                if "overloaded" in error_str.lower() or "529" in error_str:
                    if attempt < len(retry_delays):
                        delay = retry_delays[attempt]
                        logger.warning(f"🔄 Claude API overloaded (attempt {attempt + 1}/{len(retry_delays) + 1}), retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"❌ Claude API still overloaded after {len(retry_delays) + 1} attempts (total wait: {sum(retry_delays)}s)")
                        raise Exception(f"Claude API overloaded after {len(retry_delays) + 1} retries over {sum(retry_delays)} seconds. Skipping Claude analysis.")
                
                # For other errors (including 429 rate limits), don't retry - fail immediately
                logger.error(f"❌ Claude API call failed: {e}")
                logger.error(f"Available client methods: {dir(self.client)}")
                raise
        
        # Should never reach here, but just in case
        raise Exception("Unexpected error in Claude API retry logic")
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                analysis = json.loads(json_match.group())
                return self._validate_analysis(analysis)
            else:
                logger.warning("⚠️ No JSON found in response, using fallback parser")
                return self._parse_text_response(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON parsing failed: {e}, using fallback parser")
            return self._parse_text_response(response_text)
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis data"""
        
        # Default values
        defaults = {
            'overall_score': 7.0,
            'recommendation': 'Consider',
            'one_line_verdict': 'A screenplay with potential that needs development.',
            'executive_summary': 'Analysis in progress.',
            'structural_analysis': 'Structural assessment pending.',
            'character_analysis': 'Character evaluation pending.',
            'thematic_depth': 'Thematic analysis pending.',
            'craft_evaluation': 'Craft assessment pending.',
            'genre_mastery': 'Genre analysis pending.',
            'top_strengths': [],
            'key_weaknesses': [],
            'improvement_strategies': [],
            'commercial_viability': 'Market potential to be determined.',
            'target_audience': 'General audience.',
            'comparable_films': [],
            'casting_vision': [],
            'confidence': 0.75
        }
        
        # Apply defaults for missing fields
        for key, default_value in defaults.items():
            if key not in analysis:
                analysis[key] = default_value
        
        # Validate score range
        analysis['overall_score'] = max(0, min(10, float(analysis['overall_score'])))
        
        # Validate recommendation
        valid_recs = ['Pass', 'Consider', 'Recommend', 'Strong Recommend']
        if analysis['recommendation'] not in valid_recs:
            score = analysis['overall_score']
            if score < 5:
                analysis['recommendation'] = 'Pass'
            elif score < 7:
                analysis['recommendation'] = 'Consider'
            elif score < 8.5:
                analysis['recommendation'] = 'Recommend'
            else:
                analysis['recommendation'] = 'Strong Recommend'
        
        # Validate lists
        list_fields = ['top_strengths', 'key_weaknesses', 'improvement_strategies', 'comparable_films']
        for field in list_fields:
            if not isinstance(analysis[field], list):
                analysis[field] = []
            # Filter out empty items
            analysis[field] = [item for item in analysis[field] if isinstance(item, str) and len(item.strip()) > 5]
        
        # Validate casting vision
        if not isinstance(analysis['casting_vision'], list):
            analysis['casting_vision'] = []
        
        validated_casting = []
        for suggestion in analysis['casting_vision']:
            if isinstance(suggestion, dict) and 'character' in suggestion and 'actors' in suggestion:
                if isinstance(suggestion['actors'], list):
                    validated_casting.append({
                        'character': suggestion['character'],
                        'actors': suggestion['actors'][:3],  # Limit to 3 actors
                        'reasoning': suggestion.get('reasoning', '')
                    })
        
        analysis['casting_vision'] = validated_casting[:5]  # Limit to 5 characters
        
        # Validate confidence
        analysis['confidence'] = max(0, min(1, float(analysis.get('confidence', 0.75))))
        
        return analysis
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Fallback text parser when JSON parsing fails"""
        
        analysis = {
            'overall_score': 7.0,
            'recommendation': 'Consider',
            'one_line_verdict': 'A screenplay with potential that needs development.',
            'executive_summary': 'Analysis in progress.',
            'top_strengths': [],
            'key_weaknesses': [],
            'suggestions': [],
            'commercial_viability': 'Market potential to be determined.',
            'target_audience': 'General audience.',
            'comparable_films': [],
            'casting_suggestions': [],
            'confidence': 0.7
        }
        
        # Try to extract score
        import re
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*[/\\]\s*10', text)
        if score_match:
            analysis['overall_score'] = float(score_match.group(1))
        
        # Try to extract one-line verdict
        verdict_match = re.search(r'(?:verdict|summary):\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if verdict_match:
            analysis['one_line_verdict'] = verdict_match.group(1).strip()
        
        return analysis
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)
    
    def to_database_format(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert analysis result to database format"""
        # Get the analysis data from the raw response
        analysis_data = {}
        if result.raw_api_response:
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', result.raw_api_response)
                if json_match:
                    analysis_data = json.loads(json_match.group())
            except:
                pass
        
        return {
            'id': result.id,
            'title': result.title,
            'genre': result.genre,
            'detected_genre': result.detected_genre,
            'subgenre': result.subgenre,
            'overall_score': result.overall_score,
            'recommendation': result.recommendation,
            'one_line_verdict': result.one_line_verdict,
            'logline': result.logline,
            'executive_summary': result.executive_summary,
            'structural_analysis': analysis_data.get('structural_analysis', ''),
            'character_analysis': analysis_data.get('character_analysis', ''),
            'thematic_depth': analysis_data.get('thematic_depth', ''),
            'craft_evaluation': analysis_data.get('craft_evaluation', ''),
            'genre_mastery': analysis_data.get('genre_mastery', ''),
            'top_strengths': json.dumps(result.top_strengths),
            'key_weaknesses': json.dumps(result.key_weaknesses),
            'suggestions': json.dumps(result.suggestions),  # Keep for backward compatibility
            'improvement_strategies': json.dumps(analysis_data.get('improvement_strategies', [])),
            'commercial_viability': result.commercial_viability,
            'target_audience': result.target_audience,
            'comparable_films': json.dumps(result.comparable_films),
            'casting_suggestions': json.dumps(result.casting_suggestions),  # Keep for backward compatibility
            'casting_vision': json.dumps(analysis_data.get('casting_vision', [])),
            'director_recommendation': result.director_recommendation,
            'ai_model': result.ai_model,
            'confidence_level': result.confidence_level,
            'processing_time': result.processing_time,
            'cost': result.cost,
            'status': 'completed',
            'raw_api_request': result.raw_api_request,
            'raw_api_response': result.raw_api_response
        }
