#!/usr/bin/env python3
"""
PiAPI Image Generation Integration
Generates Hollywood-quality movie posters using PiAPI
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PiAPIResult:
    """PiAPI poster generation result"""
    poster_url: Optional[str]
    generation_prompt: str
    processing_time: float
    cost: float
    success: bool
    error_message: Optional[str] = None

class PiAPIAnalyzer:
    """PiAPI integration for Hollywood movie poster generation"""
    
    def __init__(self):
        self.api_key = os.getenv("PIAPI_API_KEY")
        self.api_url = "https://api.piapi.ai/api/v1/task"  # PiAPI task endpoint
        
        # PiAPI Flux pricing (estimated)
        self.cost_per_image = 0.02  # $0.02 per image generation
        
        if not self.api_key:
            logger.warning("⚠️  PIAPI temporarily disabled - PiAPI poster generation will be disabled")
        else:
            logger.info("🎨 PiAPI Analyzer initialized for Hollywood poster generation")
    
    async def generate_poster(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> Optional[PiAPIResult]:
        """Generate Hollywood movie poster using PiAPI"""
        
        if not self.api_key:
            logger.warning("❌ PiAPI poster generation skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create Hollywood-style prompt based on genre and analysis
            prompt = self._create_poster_prompt(title, genre, analysis_data)
            
            # Call PiAPI to generate poster
            poster_url = await self._call_piapi(prompt, title)
            
            processing_time = time.time() - start_time
            
            result = PiAPIResult(
                poster_url=poster_url,
                generation_prompt=prompt,
                processing_time=processing_time,
                cost=self.cost_per_image,
                success=poster_url is not None,
                error_message=None if poster_url else "Image generation failed"
            )
            
            if result.success:
                logger.info(f"🎨 PiAPI poster generated in {processing_time:.2f}s")
                logger.info(f"💰 PiAPI cost: ${result.cost:.4f}")
                logger.info(f"🖼️  Poster URL: {poster_url}")
            else:
                logger.error(f"❌ PiAPI poster generation failed")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ PiAPI poster generation failed: {e}")
            return PiAPIResult(
                poster_url=None,
                generation_prompt="",
                processing_time=0,
                cost=0,
                success=False,
                error_message=str(e)
            )
    
    def _create_poster_prompt(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> str:
        """Create Hollywood-quality poster generation prompt for PiAPI Flux"""
        
        score = analysis_data.get('score', 5.0)
        poster_style = analysis_data.get('poster_style', 'theatrical')
        
        # Enhanced genre-specific styling for Hollywood quality
        genre_styles = {
            'horror': "dark atmospheric horror movie poster, deep shadows, blood-red accents, gothic typography, haunting silhouettes, supernatural elements, psychological tension",
            'thriller': "suspenseful thriller movie poster, dramatic chiaroscuro lighting, urban noir aesthetic, tension-filled composition, mysterious shadows, high contrast",
            'comedy': "vibrant comedy movie poster, bright saturated colors, playful typography, energetic character poses, whimsical elements, cheerful atmosphere",
            'action': "explosive action movie poster, dynamic motion blur, heroic character poses, dramatic lighting, high-energy composition, metallic textures",
            'drama': "emotional drama movie poster, intimate character portraits, subtle lighting, artistic composition, human connection themes, award-season aesthetic",
            'sci-fi': "futuristic sci-fi movie poster, high-tech aesthetic, neon lighting, space elements, advanced technology, cyberpunk influences",
            'fantasy': "epic fantasy movie poster, magical elements, mystical lighting, otherworldly creatures, enchanted landscapes, medieval influences",
            'western': "classic western movie poster, dusty landscapes, dramatic silhouettes, vintage typography, frontier aesthetic, golden hour desert lighting"
        }
        
        style = genre_styles.get(genre.lower(), "professional Hollywood movie poster, cinematic composition, dramatic lighting, theatrical quality")
        
        # Quality tier based on analysis score
        if score >= 9.0:
            quality_tier = "Oscar-caliber masterpiece"
        elif score >= 8.0:
            quality_tier = "award-winning blockbuster"
        elif score >= 7.0:
            quality_tier = "major studio theatrical release"
        elif score >= 6.0:
            quality_tier = "professional theatrical release"
        else:
            quality_tier = "indie artistic vision"
        
        # Create enhanced prompt for PiAPI Flux
        prompt = f"""**HOLLYWOOD MOVIE POSTER - PROFESSIONAL QUALITY**

**FILM:** "{title}" - {quality_tier} {genre} film

**VISUAL STYLE:** {style}

**TECHNICAL REQUIREMENTS:**
- Movie poster aspect ratio (27x40 inches / 2:3 ratio)
- PERFECT title typography with "{title}" prominently displayed
- Professional movie poster layout and hierarchy
- Theatrical distribution quality
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

**OUTPUT:** Photorealistic, high-quality movie poster that could be used for actual theatrical release, with flawless title typography and professional Hollywood marketing standards. Style: {poster_style}"""
        
        return prompt
    
    async def _call_piapi(self, prompt: str, title: str) -> Optional[str]:
        """Call PiAPI to generate poster image using Flux model"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # PiAPI task creation payload for Flux
            payload = {
                "model": "flux",  # Use PiAPI's Flux model
                "task_type": "text-to-image",
                "input": {
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1792,  # Movie poster aspect ratio
                    "steps": 30,
                    "guidance_scale": 7.5,
                    "seed": -1,  # Random seed
                    "safety_checker": True
                }
            }
            
            logger.info(f"🔄 Creating PiAPI Flux task for '{title}'...")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Create task
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    task_id = result_data.get('task_id')
                    
                    if not task_id:
                        logger.error("❌ No task_id returned from PiAPI")
                        return None
                    
                    logger.info(f"✅ PiAPI task created: {task_id}")
                    
                    # Poll for completion
                    return await self._poll_task_completion(task_id, title, headers, client)
                
                else:
                    logger.error(f"❌ PiAPI task creation failed: {response.status_code} - {response.text}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ PiAPI call failed: {e}")
            return None
    
    async def _poll_task_completion(self, task_id: str, title: str, headers: dict, client: httpx.AsyncClient) -> Optional[str]:
        """Poll for task completion if async processing is used"""
        
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            await asyncio.sleep(10)  # Wait 10 seconds between checks
            attempt += 1
            
            try:
                # Check task status
                status_response = await client.get(
                    f"https://api.piapi.ai/api/v1/task/{task_id}",
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    logger.error(f"❌ Failed to check task status: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                logger.info(f"🔄 Task {task_id} status: {status} (attempt {attempt}/{max_attempts})")
                
                if status == 'completed':
                    # Get the generated image URL
                    if 'output' in status_data and 'images' in status_data['output']:
                        images = status_data['output']['images']
                        if images and len(images) > 0:
                            image_url = images[0]
                            logger.info(f"✅ PiAPI poster generated: {image_url}")
                            
                            # Save image locally
                            saved_url = await self._save_poster_image(image_url, title)
                            return saved_url or image_url
                    
                    logger.error("❌ No images in completed task")
                    return None
                
                elif status == 'failed':
                    error_msg = status_data.get('error', 'Unknown error')
                    logger.error(f"❌ PiAPI task failed: {error_msg}")
                    return None
                
                # Continue polling if status is 'pending' or 'processing'
                
            except Exception as e:
                logger.error(f"❌ Error polling task status: {e}")
                continue
        
        logger.error(f"❌ PiAPI task timed out after {max_attempts} attempts")
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
            filename = f"piapi_{safe_title}_{int(time.time())}.png"
            filepath = os.path.join(poster_dir, filename)
            
            logger.info(f"🔄 Downloading PiAPI poster from: {image_url}")
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
                        logger.info(f"✅ PiAPI poster saved: {relative_url} ({os.path.getsize(filepath)} bytes)")
                        return relative_url
                    else:
                        logger.error(f"❌ File not saved or empty: {filepath}")
                        return None
                else:
                    logger.error(f"❌ Failed to download image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to save PiAPI poster image: {e}")
            return None
    
    def to_database_format(self, result: PiAPIResult) -> Dict[str, Any]:
        """Convert PiAPIResult to database format"""
        return {
            'piapi_poster_url': result.poster_url,
            'piapi_poster_prompt': result.generation_prompt,
            'piapi_poster_cost': result.cost,
            'piapi_poster_success': result.success,
            'piapi_poster_error': result.error_message
        }
