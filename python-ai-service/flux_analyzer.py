#!/usr/bin/env python3
"""
Flux Pro Image Generation Integration via Replicate
Generates Hollywood-quality movie posters using Flux Pro
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
class FluxResult:
    """Flux Pro poster generation result"""
    poster_url: Optional[str]
    generation_prompt: str
    processing_time: float
    cost: float
    success: bool
    error_message: Optional[str] = None

class FluxAnalyzer:
    """Flux Pro integration for Hollywood movie poster generation via Replicate"""
    
    def __init__(self):
        self.api_key = os.getenv("REPLICATE_API_TOKEN")
        self.api_url = "https://api.replicate.com/v1/predictions"
        
        # Flux Pro pricing (Replicate)
        self.cost_per_image = 0.055  # $0.055 per image generation
        
        if not self.api_key:
            logger.warning("⚠️  REPLICATE_API_TOKEN not set - Flux Pro poster generation will be disabled")
        else:
            logger.info("🎨 Flux Pro Analyzer initialized for Hollywood poster generation")
    
    async def generate_poster(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> Optional[FluxResult]:
        """Generate Hollywood movie poster using Flux Pro"""
        
        if not self.api_key:
            logger.warning("❌ Flux Pro poster generation skipped - no API key")
            return None
            
        try:
            start_time = time.time()
            
            # Create Hollywood-style prompt based on genre and analysis
            prompt = self._create_poster_prompt(title, genre, analysis_data)
            
            # Call Replicate API to generate poster
            poster_url = await self._call_replicate_api(prompt, title)
            
            processing_time = time.time() - start_time
            
            result = FluxResult(
                poster_url=poster_url,
                generation_prompt=prompt,
                processing_time=processing_time,
                cost=self.cost_per_image,
                success=poster_url is not None,
                error_message=None if poster_url else "Image generation failed"
            )
            
            if result.success:
                logger.info(f"🎨 Flux Pro poster generated in {processing_time:.2f}s")
                logger.info(f"💰 Flux Pro cost: ${result.cost:.4f}")
                logger.info(f"🖼️  Poster URL: {poster_url}")
            else:
                logger.error(f"❌ Flux Pro poster generation failed")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Flux Pro poster generation failed: {e}")
            return FluxResult(
                poster_url=None,
                generation_prompt="",
                processing_time=0,
                cost=0,
                success=False,
                error_message=str(e)
            )
    
    def _create_poster_prompt(self, title: str, genre: str, analysis_data: Dict[str, Any]) -> str:
        """Create advanced Hollywood-style poster generation prompt"""
        
        score = analysis_data.get('score', 5.0)
        recommendation = analysis_data.get('recommendation', 'Consider')
        themes = analysis_data.get('themes', [])
        tone = analysis_data.get('tone', 'dramatic')
        
        # Advanced genre-specific styling with cinematic references
        genre_styles = {
            'horror': {
                'style': "dark atmospheric horror movie poster, deep shadows, blood-red accents, gothic typography, haunting silhouettes, supernatural dread, psychological horror elements",
                'mood': "terrifying, ominous, spine-chilling, supernatural",
                'lighting': "dramatic chiaroscuro, deep shadows, strategic red lighting",
                'reference': "The Conjuring, Hereditary, Midsommar poster aesthetic"
            },
            'thriller': {
                'style': "suspenseful thriller poster, noir cinematography, urban tension, mysterious shadows, psychological intensity, crime drama elements",
                'mood': "suspenseful, tense, mysterious, gripping",
                'lighting': "high contrast noir lighting, dramatic shadows, neon accents",
                'reference': "Seven, Gone Girl, Zodiac poster design language"
            },
            'comedy': {
                'style': "vibrant comedy poster, bright saturated colors, playful character poses, whimsical typography, energetic composition, comedic visual elements",
                'mood': "joyful, energetic, playful, uplifting",
                'lighting': "bright cheerful lighting, warm sunny tones, vibrant colors",
                'reference': "The Grand Budapest Hotel, Superbad, Knives Out poster style"
            },
            'romantic comedy': {
                'style': "romantic comedy poster, soft romantic lighting, charming character chemistry, elegant typography, heart-warming visual metaphors, dreamy atmosphere",
                'mood': "romantic, charming, heartwarming, delightful",
                'lighting': "soft golden hour lighting, warm romantic glow, pastel tones",
                'reference': "The Proposal, Crazy Rich Asians, La La Land poster aesthetics"
            },
            'action': {
                'style': "explosive action poster, dynamic motion, heroic poses, dramatic lighting, high-energy composition, metallic textures, adrenaline-fueled imagery",
                'mood': "intense, explosive, heroic, adrenaline-pumping",
                'lighting': "dramatic action lighting, explosive effects, metallic highlights",
                'reference': "Mad Max Fury Road, John Wick, Mission Impossible poster design"
            },
            'adventure': {
                'style': "epic adventure poster, sweeping landscapes, heroic journey imagery, golden hour lighting, majestic scale, exploration themes, mythic storytelling",
                'mood': "epic, adventurous, heroic, inspiring",
                'lighting': "epic golden hour lighting, sweeping vistas, adventure atmosphere",
                'reference': "Indiana Jones, The Lord of the Rings, Pirates of the Caribbean poster style"
            },
            'drama': {
                'style': "emotional drama poster, intimate character portraits, subtle artistic lighting, sophisticated composition, human connection themes, award-season quality",
                'mood': "emotional, intimate, profound, moving",
                'lighting': "subtle dramatic lighting, warm emotional tones, artistic shadows",
                'reference': "Moonlight, Manchester by the Sea, The Shape of Water poster design"
            },
            'sci-fi': {
                'style': "futuristic sci-fi poster, high-tech aesthetic, neon lighting, space elements, advanced technology, cyberpunk influences, holographic effects, cosmic imagery",
                'mood': "futuristic, mysterious, technological, otherworldly",
                'lighting': "neon sci-fi lighting, electric blues, holographic effects, cosmic atmosphere",
                'reference': "Blade Runner 2049, Arrival, Ex Machina poster aesthetics"
            },
            'fantasy': {
                'style': "epic fantasy poster, magical elements, mystical lighting, otherworldly creatures, enchanted landscapes, medieval influences, mythological themes",
                'mood': "magical, mystical, epic, enchanting",
                'lighting': "mystical magical lighting, ethereal glows, enchanted atmosphere",
                'reference': "The Lord of the Rings, Game of Thrones, Pan's Labyrinth poster design"
            },
            'western': {
                'style': "classic western poster, dusty frontier landscapes, dramatic silhouettes, vintage typography, frontier aesthetic, golden hour desert lighting, cowboy mythology",
                'mood': "rugged, frontier, classic, timeless",
                'lighting': "golden hour desert lighting, dusty atmosphere, classic western tones",
                'reference': "The Good, The Bad and The Ugly, True Grit, Hell or High Water poster style"
            }
        }
        
        # Get genre-specific styling or default
        style_info = genre_styles.get(genre.lower(), {
            'style': "professional Hollywood movie poster, cinematic composition, dramatic lighting, theatrical quality",
            'mood': "dramatic, cinematic, professional",
            'lighting': "professional cinematic lighting, dramatic shadows",
            'reference': "classic Hollywood poster design"
        })
        
        # Quality tier based on analysis score
        if score >= 9.0:
            quality_tier = "Oscar-caliber masterpiece"
            production_notes = "A24 arthouse meets Marvel blockbuster production value"
        elif score >= 8.0:
            quality_tier = "award-winning blockbuster"
            production_notes = "major studio theatrical release quality"
        elif score >= 7.0:
            quality_tier = "professional theatrical release"
            production_notes = "mid-budget studio production value"
        elif score >= 6.0:
            quality_tier = "solid commercial release"
            production_notes = "independent studio quality"
        else:
            quality_tier = "indie artistic vision"
            production_notes = "festival circuit aesthetic"
        
        # Create advanced Flux Pro optimized prompt
        prompt = f"""Cinematic movie poster for "{title}" - {quality_tier} {genre} film.

{style_info['style']}, {style_info['mood']} atmosphere, {style_info['lighting']}.

Professional theatrical one-sheet design, 27x40 aspect ratio, high-resolution digital art, elegant movie title typography, {production_notes}.

Inspired by {style_info['reference']}, sophisticated graphic design, striking visual hierarchy, compelling composition, genre-appropriate mood and atmosphere, Hollywood marketing appeal.

Technical quality: Professional poster design studio standard, theatrical marketing campaign quality, visually compelling, commercial viability, artistic merit, award-worthy design."""
        
        return prompt
    
    async def _call_replicate_api(self, prompt: str, title: str) -> Optional[str]:
        """Call Replicate API to generate poster using Flux Pro"""
        
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Flux Pro model payload
            payload = {
                "version": "7437eed9b1e174db2c9b6e8d0d4c5de6b9c2b0e8f4a6c3d1e2f3a4b5c6d7e8f9",  # Flux Pro latest version
                "input": {
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1792,  # Movie poster aspect ratio
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50,
                    "seed": None,  # Random seed
                    "output_format": "png",
                    "output_quality": 95
                }
            }
            
            logger.info(f"🔄 Creating Flux Pro prediction for '{title}'...")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Create prediction
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 201:
                    logger.error(f"❌ Flux Pro prediction creation failed: {response.status_code} - {response.text}")
                    return None
                
                prediction_data = response.json()
                prediction_id = prediction_data.get('id')
                
                if not prediction_id:
                    logger.error("❌ No prediction ID returned from Replicate")
                    return None
                
                logger.info(f"✅ Flux Pro prediction created: {prediction_id}")
                
                # Poll for completion
                max_attempts = 60  # 10 minutes max
                attempt = 0
                
                while attempt < max_attempts:
                    await asyncio.sleep(10)  # Wait 10 seconds between checks
                    attempt += 1
                    
                    # Check prediction status
                    status_response = await client.get(
                        f"{self.api_url}/{prediction_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code != 200:
                        logger.error(f"❌ Failed to check prediction status: {status_response.status_code}")
                        continue
                    
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    logger.info(f"🔄 Prediction {prediction_id} status: {status} (attempt {attempt}/{max_attempts})")
                    
                    if status == 'succeeded':
                        # Get the generated image URL
                        output = status_data.get('output')
                        if output and len(output) > 0:
                            image_url = output[0]
                            logger.info(f"✅ Flux Pro poster generated: {image_url}")
                            
                            # Save image locally
                            saved_url = await self._save_poster_image(image_url, title)
                            return saved_url or image_url
                        else:
                            logger.error("❌ No output in succeeded prediction")
                            return None
                    
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        logger.error(f"❌ Flux Pro prediction failed: {error_msg}")
                        return None
                    
                    # Continue polling if status is 'starting' or 'processing'
                
                logger.error(f"❌ Flux Pro prediction timed out after {max_attempts} attempts")
                return None
                
        except Exception as e:
            logger.error(f"❌ Flux Pro API call failed: {e}")
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
            filename = f"flux_{safe_title}_{int(time.time())}.png"
            filepath = os.path.join(poster_dir, filename)
            
            logger.info(f"🔄 Downloading Flux Pro poster from: {image_url}")
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
                        logger.info(f"✅ Flux Pro poster saved: {relative_url} ({os.path.getsize(filepath)} bytes)")
                        return relative_url
                    else:
                        logger.error(f"❌ File not saved or empty: {filepath}")
                        return None
                else:
                    logger.error(f"❌ Failed to download image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to save Flux Pro poster image: {e}")
            return None
    
    def to_database_format(self, result: FluxResult) -> Dict[str, Any]:
        """Convert FluxResult to database format"""
        return {
            'flux_poster_url': result.poster_url,
            'flux_poster_prompt': result.generation_prompt,
            'flux_poster_cost': result.cost,
            'flux_poster_success': result.success,
            'flux_poster_error': result.error_message
        }
