#!/usr/bin/env python3
"""
Source Material Detection and Analysis
Detects and analyzes source material (books, true stories, existing IP) from screenplay title pages
"""

import os
import re
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
class SourceMaterialResult:
    """Source material analysis result"""
    has_source_material: bool
    source_type: Optional[str]  # 'book', 'true_story', 'existing_ip', 'remake', 'adaptation', 'original'
    source_title: Optional[str]
    source_author: Optional[str]
    source_description: Optional[str]
    adaptation_notes: Optional[str]
    commercial_implications: Optional[str]
    legal_considerations: Optional[str]
    market_advantages: List[str]
    potential_challenges: List[str]
    confidence_score: float  # 0-1
    raw_detection_text: str
    processing_time: float
    cost: float
    success: bool
    error_message: Optional[str] = None

class SourceMaterialAnalyzer:
    """AI-powered source material detection and analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"  # Use GPT-4o for better text analysis
        
        # Pricing for GPT-4o
        self.input_cost_per_token = 0.0025 / 1000   # $0.0025 per 1K input tokens
        self.output_cost_per_token = 0.01 / 1000    # $0.01 per 1K output tokens
        
        if not self.api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set - Source material analysis will be disabled")
        else:
            logger.info("📚 Source Material Analyzer initialized")
    
    async def analyze_source_material(self, screenplay_text: str, title: str) -> Optional[SourceMaterialResult]:
        """Analyze screenplay for source material information"""
        
        if not self.api_key:
            logger.warning("❌ Source material analysis skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Extract title page and first few pages for analysis
            title_page_text = self._extract_title_page_content(screenplay_text)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(title_page_text, title)
            
            # Call OpenAI API
            response = await self._call_openai_api(prompt)
            
            # Parse response
            analysis_data = self._parse_response(response)
            
            # Calculate cost
            input_tokens = self._estimate_tokens(prompt)
            output_tokens = self._estimate_tokens(response)
            cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
            
            processing_time = time.time() - start_time
            
            result = SourceMaterialResult(
                has_source_material=analysis_data.get('has_source_material', False),
                source_type=analysis_data.get('source_type'),
                source_title=analysis_data.get('source_title'),
                source_author=analysis_data.get('source_author'),
                source_description=analysis_data.get('source_description'),
                adaptation_notes=analysis_data.get('adaptation_notes'),
                commercial_implications=analysis_data.get('commercial_implications'),
                legal_considerations=analysis_data.get('legal_considerations'),
                market_advantages=analysis_data.get('market_advantages', []),
                potential_challenges=analysis_data.get('potential_challenges', []),
                confidence_score=analysis_data.get('confidence_score', 0.0),
                raw_detection_text=title_page_text,
                processing_time=processing_time,
                cost=cost,
                success=True,
                error_message=None
            )
            
            logger.info(f"📚 Source material analysis complete in {processing_time:.2f}s")
            logger.info(f"💰 Cost: ${cost:.4f}")
            
            if result.has_source_material:
                logger.info(f"🔍 Detected source material: {result.source_type} - '{result.source_title}'")
            else:
                logger.info("📝 No source material detected - appears to be original work")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Source material analysis failed: {e}")
            return SourceMaterialResult(
                has_source_material=False,
                source_type=None,
                source_title=None,
                source_author=None,
                source_description=None,
                adaptation_notes=None,
                commercial_implications=None,
                legal_considerations=None,
                market_advantages=[],
                potential_challenges=[],
                confidence_score=0.0,
                raw_detection_text="",
                processing_time=0,
                cost=0,
                success=False,
                error_message=str(e)
            )
    
    def _extract_title_page_content(self, screenplay_text: str) -> str:
        """Extract title page and relevant content for source material detection"""
        
        # Take first 3000 characters which should include title page and opening
        title_page_content = screenplay_text[:3000]
        
        # Look for common source material indicators
        source_indicators = [
            r"based on",
            r"adapted from",
            r"from the novel",
            r"from the book",
            r"true story",
            r"inspired by",
            r"from the play",
            r"remake of",
            r"based upon",
            r"from the memoir",
            r"from the biography",
            r"from the autobiography",
            r"from the short story",
            r"from the comic",
            r"from the graphic novel",
            r"from the video game",
            r"from the podcast",
            r"from the article",
            r"from the news story",
            r"from the documentary",
            r"from the television series",
            r"from the film",
            r"from the movie",
            r"intellectual property",
            r"franchise",
            r"sequel to",
            r"prequel to",
            r"spin-off",
            r"reboot of"
        ]
        
        # If we find indicators, expand the search area
        for indicator in source_indicators:
            if re.search(indicator, title_page_content, re.IGNORECASE):
                # Take more content if we find indicators
                title_page_content = screenplay_text[:5000]
                break
        
        return title_page_content
    
    def _create_analysis_prompt(self, title_page_text: str, title: str) -> str:
        """Create comprehensive source material analysis prompt"""
        
        return f"""You are a Hollywood development executive and legal expert analyzing a screenplay's title page and opening for source material information.

SCREENPLAY TITLE: "{title}"

TITLE PAGE AND OPENING CONTENT:
{title_page_text}

ANALYSIS TASK:
Carefully analyze this content to determine if this screenplay is based on existing source material or is an original work.

Look for indicators such as:
- "Based on" / "Adapted from" / "From the novel/book/play"
- "True story" / "Inspired by true events"
- "From the memoir/biography/autobiography"
- References to existing books, plays, films, TV shows
- Comic book/graphic novel adaptations
- Video game adaptations
- Remake/reboot/sequel indicators
- Franchise or IP references
- Author credits beyond the screenwriter
- Publisher information
- Copyright notices for source material

RESPOND WITH VALID JSON:
{{
    "has_source_material": boolean,
    "source_type": "book|true_story|existing_ip|remake|adaptation|sequel|prequel|comic|video_game|play|memoir|biography|article|podcast|original|unknown",
    "source_title": "exact title of source material or null",
    "source_author": "author/creator name or null",
    "source_description": "brief description of the source material",
    "adaptation_notes": "notes about the adaptation approach",
    "commercial_implications": "how this affects commercial potential",
    "legal_considerations": "potential legal/rights issues to consider",
    "market_advantages": ["list", "of", "market", "advantages"],
    "potential_challenges": ["list", "of", "potential", "challenges"],
    "confidence_score": 0.0-1.0
}}

COMMERCIAL ANALYSIS GUIDELINES:
- Existing IP/franchises: Higher commercial potential, built-in audience
- True stories: Awards potential, prestige, but fact-checking needed
- Book adaptations: Proven audience, but adaptation challenges
- Remakes: Nostalgia factor, but originality concerns
- Original works: Creative freedom, but no built-in audience

Be thorough but concise. If no clear source material is indicated, mark as "original"."""
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API for source material analysis"""
        
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
                        "content": "You are an expert Hollywood development executive and entertainment lawyer specializing in source material analysis and IP evaluation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Lower temperature for more consistent analysis
                "max_completion_tokens": 1500,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('choices') and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        raise Exception("No response content from OpenAI")
                else:
                    error_text = response.text
                    raise Exception(f"OpenAI API error {response.status_code}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            raise
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured data"""
        
        try:
            # Clean the response
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            # Validate required fields
            if 'has_source_material' not in data:
                data['has_source_material'] = False
            
            if 'confidence_score' not in data:
                data['confidence_score'] = 0.5
            
            # Ensure confidence score is between 0 and 1
            data['confidence_score'] = max(0.0, min(1.0, float(data.get('confidence_score', 0.5))))
            
            # Ensure lists are actually lists
            if not isinstance(data.get('market_advantages'), list):
                data['market_advantages'] = []
            
            if not isinstance(data.get('potential_challenges'), list):
                data['potential_challenges'] = []
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            
            # Return default structure
            return {
                'has_source_material': False,
                'source_type': 'unknown',
                'source_title': None,
                'source_author': None,
                'source_description': 'Failed to parse analysis response',
                'adaptation_notes': None,
                'commercial_implications': None,
                'legal_considerations': None,
                'market_advantages': [],
                'potential_challenges': [],
                'confidence_score': 0.0
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for cost calculation"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def to_database_format(self, result: SourceMaterialResult) -> Dict[str, Any]:
        """Convert SourceMaterialResult to database format"""
        return {
            'source_has_material': bool(result.has_source_material) if result.has_source_material is not None else None,
            'source_type': str(result.source_type) if result.source_type else None,
            'source_title': str(result.source_title) if result.source_title else None,
            'source_author': str(result.source_author) if result.source_author else None,
            'source_description': str(result.source_description) if result.source_description else None,
            'source_adaptation_notes': str(result.adaptation_notes) if result.adaptation_notes else None,
            'source_commercial_implications': str(result.commercial_implications) if result.commercial_implications else None,
            'source_legal_considerations': str(result.legal_considerations) if result.legal_considerations else None,
            'source_market_advantages': json.dumps(result.market_advantages) if result.market_advantages else None,
            'source_potential_challenges': json.dumps(result.potential_challenges) if result.potential_challenges else None,
            'source_confidence_score': float(result.confidence_score) if result.confidence_score is not None else None,
            'source_raw_detection_text': str(result.raw_detection_text) if result.raw_detection_text else None,
            'source_processing_time': float(result.processing_time) if result.processing_time is not None else None,
            'source_cost': float(result.cost) if result.cost is not None else None,
            'source_success': bool(result.success) if result.success is not None else None,
            'source_error_message': str(result.error_message) if result.error_message else None
        }
