#!/usr/bin/env python3
"""
GPT-5 Screenplay Analyzer - Writing Excellence Focus
Advanced writing analysis with adaptive reasoning for professional screenplay evaluation
"""

import os
import json
import time
import logging
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
class GPT5Result:
    """GPT-5 analysis result with writing excellence focus"""
    # Core metrics
    score: float  # 0-10 overall writing quality
    recommendation: str  # Professional recommendation
    executive_assessment: str  # Quick + deep unified assessment
    
    # Writing Excellence Analysis
    character_voice_analysis: Optional[Dict[str, Any]] = None
    dialogue_authenticity: Optional[Dict[str, Any]] = None
    prose_quality: Optional[Dict[str, Any]] = None
    emotional_beat_mapping: Optional[Dict[str, Any]] = None
    
    # Professional Standards
    professional_markers: Optional[Dict[str, Any]] = None
    amateur_indicators: Optional[Dict[str, Any]] = None
    industry_comparison: Optional[Dict[str, Any]] = None
    
    # Adaptive reasoning metadata
    reasoning_depth: str = "auto"  # "quick", "deep", "hybrid"
    reasoning_tokens: int = 0
    
    # Processing metadata
    processing_time: float = 0.0
    cost: float = 0.0
    confidence: float = 0.0
    raw_response: str = ""

class GPT5Analyzer:
    """GPT-5 API integration for advanced screenplay writing analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-5-chat-latest"  # Latest GPT-5 model
        
        # GPT-5 pricing (estimated - adjust based on actual pricing)
        self.input_cost_per_token = 0.00002  # $0.02 per 1K tokens
        self.output_cost_per_token = 0.00008  # $0.08 per 1K tokens
        self.reasoning_cost_per_token = 0.00012  # $0.12 per 1K reasoning tokens
        
        if not self.api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set - GPT-5 analysis will be disabled")
        else:
            logger.info("🧠 GPT-5 Writing Excellence Analyzer initialized")
    
    async def analyze(self, screenplay_text: str, title: str, genre: str = "", budget_estimate: Optional[float] = None) -> Optional[GPT5Result]:
        """Analyze screenplay with GPT-5 writing excellence focus"""
        
        if not self.api_key:
            logger.warning("❌ GPT-5 analysis skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create adaptive writing excellence prompt
            prompt = self._create_writing_excellence_prompt(screenplay_text, title, genre, budget_estimate)
            
            # Call GPT-5 API with adaptive reasoning
            response = await self._call_gpt5_api(prompt)
            
            # Parse response with writing excellence focus
            analysis_data = self._parse_response(response)
            
            # Calculate cost including reasoning tokens
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            reasoning_tokens = analysis_data.get('_reasoning_tokens', 0)
            
            cost = (
                (input_tokens * self.input_cost_per_token) + 
                (output_tokens * self.output_cost_per_token) +
                (reasoning_tokens * self.reasoning_cost_per_token)
            )
            
            processing_time = time.time() - start_time
            
            result = GPT5Result(
                score=analysis_data.get('score', 5.0),
                recommendation=analysis_data.get('recommendation', 'Consider'),
                executive_assessment=analysis_data.get('executive_assessment', ''),
                character_voice_analysis=analysis_data.get('character_voice_analysis'),
                dialogue_authenticity=analysis_data.get('dialogue_authenticity'),
                prose_quality=analysis_data.get('prose_quality'),
                emotional_beat_mapping=analysis_data.get('emotional_beat_mapping'),
                professional_markers=analysis_data.get('professional_markers'),
                amateur_indicators=analysis_data.get('amateur_indicators'),
                industry_comparison=analysis_data.get('industry_comparison'),
                reasoning_depth=analysis_data.get('reasoning_depth', 'auto'),
                reasoning_tokens=reasoning_tokens,
                processing_time=processing_time,
                cost=cost,
                confidence=analysis_data.get('confidence', 0.8),
                raw_response=response
            )
            
            logger.info(f"🧠 GPT-5 analysis completed in {processing_time:.2f}s")
            logger.info(f"💰 GPT-5 cost: ${cost:.4f} (reasoning: {reasoning_tokens} tokens)")
            logger.info(f"⭐ GPT-5 score: {result.score}/10 ({result.recommendation})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ GPT-5 analysis failed: {e}")
            return None
    
    def _create_writing_excellence_prompt(self, screenplay_text: str, title: str, genre: str, budget_estimate: Optional[float] = None) -> str:
        """Create adaptive writing excellence prompt for GPT-5"""
        
        # Truncate if too long (GPT-5 has large context but we want efficiency)
        max_chars = 200000  # Use substantial context for full analysis
        if len(screenplay_text) > max_chars:
            screenplay_text = screenplay_text[:max_chars] + "\n\n[TRUNCATED FOR ANALYSIS]"
        
        # Enhanced budget context with AI estimation for writing analysis
        estimated_budget = None
        if not budget_estimate:
            estimated_budget = estimate_budget_from_screenplay(screenplay_text, title, genre or "Drama")
        
        budget_context = format_budget_context_for_ai(budget_estimate, estimated_budget)
        
        # Get budget-appropriate casting considerations for writing assessment
        budget_for_casting = budget_estimate or estimated_budget[1] if estimated_budget else 10_000_000
        casting_strategy = get_casting_suggestions_by_budget(budget_for_casting, genre or "Drama")

        return f"""You are a top-tier Hollywood script reader and development executive with 20+ years of experience evaluating screenplays for major studios. You have an exceptional eye for writing quality and can distinguish professional from amateur work instantly.

**SCREENPLAY: "{title}"**
{f"**GENRE: {genre}**" if genre else ""}
{budget_context}

**SCREENPLAY TEXT:**
{screenplay_text}

**ADAPTIVE ANALYSIS INSTRUCTIONS:**

Use your adaptive reasoning capabilities to provide both quick professional impressions AND deep analysis where complex elements require nuanced understanding. Think deeply about writing craft elements that separate professional from amateur work.

**ANALYSIS FRAMEWORK:**

## **EXECUTIVE ASSESSMENT** (Quick + Deep Unified)
Provide immediate professional impressions, then engage deeper reasoning for complex writing elements:

**QUICK SCAN:**
- Format and structure compliance
- Obvious writing strengths/weaknesses  
- Genre execution basics
- Immediate red flags or standout elements

**DEEP ANALYSIS** (engage reasoning for complex elements):
- Character psychology authenticity in dialogue
- Subtext layers and emotional undercurrents
- Professional vs amateur writing markers
- Thematic integration subtlety

## **WRITING EXCELLENCE CATEGORIES:**

### **CHARACTER VOICE ANALYSIS**
Think deeply about character distinction and authenticity:
- Does each character speak with a unique, authentic voice?
- Can you identify characters by dialogue alone (without action lines)?
- Are character voices consistent throughout the script?
- Do voices match character backgrounds, education, emotional states?
- Identify any dialogue that feels interchangeable between characters

### **DIALOGUE AUTHENTICITY**
Analyze dialogue realism and purpose:
- Does dialogue sound natural when spoken aloud?
- Is exposition handled organically or forced?
- Are there authentic speech patterns, interruptions, subtext?
- Does dialogue serve multiple purposes (character, plot, theme)?
- Identify any "on-the-nose" or overly expository dialogue

### **PROSE QUALITY** 
Evaluate action lines and visual storytelling:
- Are action lines concise, visual, and filmable?
- Does the script "show" rather than "tell"?
- Is the writing style appropriate for the genre?
- Are scene descriptions engaging and cinematic?
- Does the prose maintain proper pacing and white space?

### **EMOTIONAL BEAT MAPPING**
Trace emotional trajectory and authenticity:
- Does each scene have clear emotional purpose?
- Are emotional beats earned through proper setup?
- Is there authentic emotional progression throughout?
- Do characters react believably to emotional situations?
- Are emotional payoffs satisfying and well-prepared?

### **PROFESSIONAL STANDARDS ASSESSMENT**
Compare against industry benchmarks:
- What separates this from amateur writing?
- Which elements meet professional standards?
- What would immediately flag this as amateur work?
- How does this compare to successful scripts in the genre?
- What would need improvement for studio consideration?

**RESPONSE FORMAT (JSON):**
```json
{{
    "score": 0.0,
    "recommendation": "",
    "confidence": 0.0,
    "reasoning_depth": "auto",
    "executive_assessment": {{
        "quick_impressions": "",
        "deep_analysis": "",
        "professional_verdict": ""
    }},
    "character_voice_analysis": {{
        "voice_distinction_score": 0,
        "authenticity_rating": "",
        "character_voice_examples": [],
        "interchangeable_dialogue_issues": [],
        "voice_consistency_assessment": ""
    }},
    "dialogue_authenticity": {{
        "naturalism_score": 0,
        "exposition_handling": "",
        "subtext_quality": "",
        "speech_pattern_authenticity": "",
        "on_the_nose_examples": []
    }},
    "prose_quality": {{
        "visual_storytelling_score": 0,
        "action_line_efficiency": "",
        "cinematic_language": "",
        "pacing_through_prose": "",
        "show_vs_tell_balance": ""
    }},
    "emotional_beat_mapping": {{
        "emotional_arc_clarity": 0,
        "beat_authenticity": "",
        "setup_payoff_effectiveness": "",
        "character_reaction_believability": "",
        "emotional_progression_analysis": ""
    }},
    "professional_markers": {{
        "industry_standard_elements": [],
        "professional_craft_indicators": [],
        "studio_ready_aspects": []
    }},
    "amateur_indicators": {{
        "red_flag_elements": [],
        "craft_improvement_needs": [],
        "amateur_writing_patterns": []
    }},
    "industry_comparison": {{
        "comparable_professional_scripts": [],
        "competitive_positioning": "",
        "market_readiness_assessment": ""
    }}
}}
```

**ANALYSIS APPROACH:**
- Use adaptive reasoning to match analysis depth to complexity
- Engage deep thinking for nuanced writing craft elements
- Provide specific examples from the script
- Focus on actionable professional insights
- Maintain industry-standard evaluation criteria

Think deeply about elements that require professional expertise to evaluate properly."""

    async def _call_gpt5_api(self, prompt: str) -> str:
        """Call GPT-5 API with adaptive reasoning enabled"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a top-tier Hollywood script reader and development executive with exceptional writing analysis capabilities. Use adaptive reasoning to provide both quick professional assessments and deep analysis for complex writing craft elements."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_completion_tokens": 4000,  # Increased for comprehensive writing analysis
            "temperature": 1.0,  # GPT-5 only supports default temperature
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"GPT-5 API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            if 'choices' not in data or not data['choices']:
                raise Exception("Invalid GPT-5 API response format")
            
            return data['choices'][0]['message']['content']
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse GPT-5 response with writing excellence focus"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            
            if json_match:
                json_str = json_match.group()
                
                # Try to fix truncated JSON if needed
                json_str = self._fix_truncated_json(json_str)
                
                parsed_data = json.loads(json_str)
                
                # Validate and structure the response
                return self._validate_response(parsed_data)
            else:
                logger.warning("⚠️  No JSON found in GPT-5 response, using fallback parsing")
                return self._fallback_parse(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON parsing failed: {e}, attempting to fix")
            try:
                json_match = re.search(r'\{[\s\S]*', response)
                if json_match:
                    json_str = self._fix_truncated_json(json_match.group())
                    parsed_data = json.loads(json_str)
                    logger.info("✅ Successfully parsed truncated JSON after repair")
                    return self._validate_response(parsed_data)
            except:
                pass
            
            logger.warning("⚠️  All JSON parsing attempts failed, using fallback")
            return self._fallback_parse(response)
    
    def _fix_truncated_json(self, json_str: str) -> str:
        """Fix truncated JSON by adding missing closing braces and quotes"""
        
        # Count opening and closing braces/brackets
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # If JSON is truncated in the middle of a string value, close the string
        if json_str.count('"') % 2 == 1:
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
    
    def _validate_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure GPT-5 writing excellence response"""
        
        # Ensure basic fields exist
        validated = {
            'score': min(10.0, max(0.0, data.get('score', 5.0))),
            'recommendation': data.get('recommendation', 'Consider'),
            'confidence': min(1.0, max(0.0, data.get('confidence', 0.8))),
            'reasoning_depth': data.get('reasoning_depth', 'auto')
        }
        
        # Validate executive assessment
        if 'executive_assessment' in data:
            exec_assess = data['executive_assessment']
            validated['executive_assessment'] = {
                'quick_impressions': exec_assess.get('quick_impressions', ''),
                'deep_analysis': exec_assess.get('deep_analysis', ''),
                'professional_verdict': exec_assess.get('professional_verdict', '')
            }
        
        # Validate writing excellence categories
        writing_categories = [
            'character_voice_analysis', 'dialogue_authenticity', 
            'prose_quality', 'emotional_beat_mapping',
            'professional_markers', 'amateur_indicators', 'industry_comparison'
        ]
        
        for category in writing_categories:
            if category in data:
                validated[category] = data[category]
        
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
        
        # Extract key insights from response
        lines = response.split('\n')
        assessment = next((line.strip() for line in lines if len(line.strip()) > 30), "Analysis completed")
        
        return {
            'score': score,
            'recommendation': recommendation,
            'executive_assessment': assessment[:500],
            'confidence': 0.7,
            'reasoning_depth': 'fallback'
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for GPT-5"""
        return max(1, len(text) // 4)
    
    def to_database_format(self, result: GPT5Result) -> Dict[str, Any]:
        """Convert GPT-5 result to database format"""
        
        db_data = {
            'gpt5_score': result.score,
            'gpt5_recommendation': result.recommendation,
            'gpt5_executive_assessment': result.executive_assessment,
            'gpt5_reasoning_depth': result.reasoning_depth,
            'gpt5_reasoning_tokens': result.reasoning_tokens,
            'gpt5_confidence': result.confidence,
            'gpt5_processing_time': result.processing_time,
            'gpt5_cost': result.cost,
            'gpt5_raw_response': result.raw_response
        }
        
        # Add writing excellence analysis as JSON
        if result.character_voice_analysis:
            db_data['gpt5_character_voice_analysis'] = json.dumps(result.character_voice_analysis)
        if result.dialogue_authenticity:
            db_data['gpt5_dialogue_authenticity'] = json.dumps(result.dialogue_authenticity)
        if result.prose_quality:
            db_data['gpt5_prose_quality'] = json.dumps(result.prose_quality)
        if result.emotional_beat_mapping:
            db_data['gpt5_emotional_beat_mapping'] = json.dumps(result.emotional_beat_mapping)
        if result.professional_markers:
            db_data['gpt5_professional_markers'] = json.dumps(result.professional_markers)
        if result.amateur_indicators:
            db_data['gpt5_amateur_indicators'] = json.dumps(result.amateur_indicators)
        if result.industry_comparison:
            db_data['gpt5_industry_comparison'] = json.dumps(result.industry_comparison)
        
        return db_data
