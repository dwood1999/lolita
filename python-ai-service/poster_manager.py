#!/usr/bin/env python3
"""
Comprehensive Movie Poster Generation Manager
Orchestrates multiple AI sources and poster variations for impressive results
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import httpx
from dotenv import load_dotenv

# Import our poster generation analyzers
from openai_analyzer import OpenAIAnalyzer
from flux_analyzer import FluxAnalyzer
from piapi_analyzer import PiAPIAnalyzer

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PosterVariation:
    """Individual poster variation result"""
    source: str  # 'openai', 'flux', 'piapi'
    style: str   # 'theatrical', 'character', 'artistic', 'minimalist'
    url: Optional[str]
    prompt: str
    cost: float
    success: bool
    processing_time: float
    error_message: Optional[str] = None

@dataclass
class PosterCollection:
    """Complete poster generation result with multiple variations"""
    title: str
    genre: str
    variations: List[PosterVariation]
    total_cost: float
    total_processing_time: float
    success_count: int
    best_poster_url: Optional[str]
    best_poster_source: Optional[str]

class PosterManager:
    """Comprehensive poster generation manager with multiple sources and variations"""
    
    def __init__(self):
        # Initialize all poster generation sources
        self.openai_analyzer = OpenAIAnalyzer()
        self.flux_analyzer = FluxAnalyzer()
        self.piapi_analyzer = PiAPIAnalyzer()
        
        # Poster style variations
        self.poster_styles = {
            'theatrical': {
                'description': 'Classic theatrical one-sheet poster with dramatic composition',
                'emphasis': 'commercial appeal, theatrical marketing, dramatic lighting'
            },
            'character': {
                'description': 'Character-focused poster highlighting main protagonists',
                'emphasis': 'character portraits, emotional connection, intimate framing'
            },
            'artistic': {
                'description': 'Artistic and stylized poster with creative visual metaphors',
                'emphasis': 'artistic vision, creative composition, visual metaphors'
            },
            'minimalist': {
                'description': 'Clean, minimalist poster with strong visual impact',
                'emphasis': 'minimal design, strong typography, clean composition'
            }
        }
        
        logger.info("🎬 Poster Manager initialized with multiple sources and style variations")
    
    async def generate_poster_collection(
        self, 
        title: str, 
        genre: str, 
        analysis_data: Dict[str, Any],
        variations: List[str] = None
    ) -> PosterCollection:
        """Generate a comprehensive collection of movie posters from multiple sources"""
        
        if variations is None:
            variations = ['theatrical', 'character']  # Default to 2 main variations
        
        logger.info(f"🎨 Generating poster collection for '{title}' ({genre})")
        logger.info(f"📋 Requested variations: {', '.join(variations)}")
        
        start_time = time.time()
        all_variations = []
        
        # Generate posters from multiple sources in parallel
        tasks = []
        
        # OpenAI DALL-E 3 - Always include for high quality
        for style in variations:
            tasks.append(self._generate_openai_variation(title, genre, analysis_data, style))
        
        # Flux Pro - High quality alternative
        if self.flux_analyzer.api_key:
            for style in variations:
                tasks.append(self._generate_flux_variation(title, genre, analysis_data, style))
        
        # PiAPI - Additional source if available
        if self.piapi_analyzer.api_key:
            # Only generate one PiAPI variation to control costs
            tasks.append(self._generate_piapi_variation(title, genre, analysis_data, variations[0]))
        
        # Execute all poster generation tasks in parallel
        logger.info(f"🔄 Executing {len(tasks)} poster generation tasks in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results - ensure we capture all successful variations
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"⚠️ Poster generation task failed: {result}")
                # Create a failed variation for tracking
                all_variations.append(PosterVariation(
                    source='unknown',
                    style='unknown',
                    url=None,
                    prompt=str(result),
                    cost=0,
                    success=False,
                    processing_time=0,
                    error_message=str(result)
                ))
            elif result:
                all_variations.append(result)
            else:
                logger.warning("⚠️ Poster generation task returned None")
        
        total_processing_time = time.time() - start_time
        total_cost = sum(v.cost for v in all_variations)
        success_count = sum(1 for v in all_variations if v.success)
        
        # Determine best poster (prefer successful ones, then by source priority)
        best_poster = self._select_best_poster(all_variations)
        
        collection = PosterCollection(
            title=title,
            genre=genre,
            variations=all_variations,
            total_cost=total_cost,
            total_processing_time=total_processing_time,
            success_count=success_count,
            best_poster_url=best_poster.url if best_poster else None,
            best_poster_source=best_poster.source if best_poster else None
        )
        
        logger.info(f"✅ Poster collection complete: {success_count}/{len(all_variations)} successful")
        logger.info(f"💰 Total cost: ${total_cost:.4f}")
        logger.info(f"⏱️  Total time: {total_processing_time:.2f}s")
        
        if best_poster:
            logger.info(f"🏆 Best poster: {best_poster.source} ({best_poster.style})")
        
        return collection
    
    async def _generate_openai_variation(
        self, 
        title: str, 
        genre: str, 
        analysis_data: Dict[str, Any], 
        style: str
    ) -> Optional[PosterVariation]:
        """Generate OpenAI DALL-E 3 poster variation"""
        
        try:
            start_time = time.time()
            
            # Enhance analysis data with style-specific information
            enhanced_data = analysis_data.copy()
            enhanced_data['poster_style'] = style
            enhanced_data['style_emphasis'] = self.poster_styles[style]['emphasis']
            
            # Generate poster using OpenAI analyzer
            poster_url, prompt = await self.openai_analyzer._generate_movie_poster(
                title, genre, enhanced_data
            )
            
            processing_time = time.time() - start_time
            
            return PosterVariation(
                source='openai',
                style=style,
                url=poster_url,
                prompt=prompt or "",
                cost=0.04,  # DALL-E 3 cost
                success=poster_url is not None,
                processing_time=processing_time,
                error_message=None if poster_url else "OpenAI generation failed"
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI {style} variation failed: {e}")
            return PosterVariation(
                source='openai',
                style=style,
                url=None,
                prompt="",
                cost=0,
                success=False,
                processing_time=0,
                error_message=str(e)
            )
    
    async def _generate_flux_variation(
        self, 
        title: str, 
        genre: str, 
        analysis_data: Dict[str, Any], 
        style: str
    ) -> Optional[PosterVariation]:
        """Generate Flux Pro poster variation"""
        
        try:
            start_time = time.time()
            
            # Enhance analysis data with style-specific information
            enhanced_data = analysis_data.copy()
            enhanced_data['poster_style'] = style
            enhanced_data['style_emphasis'] = self.poster_styles[style]['emphasis']
            
            # Generate poster using Flux analyzer
            flux_result = await self.flux_analyzer.generate_poster(
                title, genre, enhanced_data
            )
            
            processing_time = time.time() - start_time
            
            if flux_result:
                return PosterVariation(
                    source='flux',
                    style=style,
                    url=flux_result.poster_url,
                    prompt=flux_result.generation_prompt,
                    cost=flux_result.cost,
                    success=flux_result.success,
                    processing_time=processing_time,
                    error_message=flux_result.error_message
                )
            else:
                return PosterVariation(
                    source='flux',
                    style=style,
                    url=None,
                    prompt="",
                    cost=0,
                    success=False,
                    processing_time=processing_time,
                    error_message="Flux analyzer returned None"
                )
            
        except Exception as e:
            logger.error(f"❌ Flux {style} variation failed: {e}")
            return PosterVariation(
                source='flux',
                style=style,
                url=None,
                prompt="",
                cost=0,
                success=False,
                processing_time=0,
                error_message=str(e)
            )
    
    async def _generate_piapi_variation(
        self, 
        title: str, 
        genre: str, 
        analysis_data: Dict[str, Any], 
        style: str
    ) -> Optional[PosterVariation]:
        """Generate PiAPI poster variation"""
        
        try:
            start_time = time.time()
            
            # Enhance analysis data with style-specific information
            enhanced_data = analysis_data.copy()
            enhanced_data['poster_style'] = style
            enhanced_data['style_emphasis'] = self.poster_styles[style]['emphasis']
            
            # Generate poster using PiAPI analyzer
            piapi_result = await self.piapi_analyzer.generate_poster(
                title, genre, enhanced_data
            )
            
            processing_time = time.time() - start_time
            
            if piapi_result:
                return PosterVariation(
                    source='piapi',
                    style=style,
                    url=piapi_result.poster_url,
                    prompt=piapi_result.generation_prompt,
                    cost=piapi_result.cost,
                    success=piapi_result.success,
                    processing_time=processing_time,
                    error_message=piapi_result.error_message
                )
            else:
                return PosterVariation(
                    source='piapi',
                    style=style,
                    url=None,
                    prompt="",
                    cost=0,
                    success=False,
                    processing_time=processing_time,
                    error_message="PiAPI analyzer returned None"
                )
            
        except Exception as e:
            logger.error(f"❌ PiAPI {style} variation failed: {e}")
            return PosterVariation(
                source='piapi',
                style=style,
                url=None,
                prompt="",
                cost=0,
                success=False,
                processing_time=0,
                error_message=str(e)
            )
    
    def _select_best_poster(self, variations: List[PosterVariation]) -> Optional[PosterVariation]:
        """Select the best poster from available variations"""
        
        # Filter successful variations
        successful = [v for v in variations if v.success]
        
        if not successful:
            return None
        
        # Priority order: OpenAI > Flux > PiAPI
        source_priority = {'openai': 3, 'flux': 2, 'piapi': 1}
        
        # Sort by success, then source priority, then style preference
        style_priority = {'theatrical': 4, 'character': 3, 'artistic': 2, 'minimalist': 1}
        
        best = max(successful, key=lambda v: (
            v.success,
            source_priority.get(v.source, 0),
            style_priority.get(v.style, 0)
        ))
        
        return best
    
    def to_database_format(self, collection: PosterCollection) -> Dict[str, Any]:
        """Convert PosterCollection to database format"""
        
        db_data = {
            'poster_collection_title': str(collection.title) if collection.title else None,
            'poster_collection_genre': str(collection.genre) if collection.genre else None,
            'poster_total_cost': float(collection.total_cost) if collection.total_cost is not None else 0.0,
            'poster_total_time': float(collection.total_processing_time) if collection.total_processing_time is not None else 0.0,
            'poster_success_count': int(collection.success_count) if collection.success_count is not None else 0,
            'poster_best_url': str(collection.best_poster_url) if collection.best_poster_url else None,
            'poster_best_source': str(collection.best_poster_source) if collection.best_poster_source else None,
            'poster_variations_json': json.dumps([
                {
                    'source': str(v.source) if v.source else None,
                    'style': str(v.style) if v.style else None,
                    'url': str(v.url) if v.url else None,
                    'prompt': str(v.prompt) if v.prompt else None,
                    'cost': float(v.cost) if v.cost is not None else 0.0,
                    'success': bool(v.success) if v.success is not None else False,
                    'processing_time': float(v.processing_time) if v.processing_time is not None else 0.0,
                    'error_message': str(v.error_message) if v.error_message else None
                }
                for v in collection.variations
            ])
        }
        
        return db_data
