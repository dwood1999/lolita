"""
Quilty Screenplay Analysis Service
Python backend for AI-powered screenplay analysis with Claude Opus 4.1
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, AsyncGenerator
import os
import json
import uuid
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import asyncio

# Import our custom modules
from database import ScreenplayDatabase
from claude_analyzer import ClaudeOpusAnalyzer, AnalysisResult
from grok_analyzer import GrokAnalyzer
from openai_analyzer import OpenAIAnalyzer
from gpt5_analyzer import GPT5Analyzer
# from piapi_analyzer import PiAPIAnalyzer  # Commented out - not working
from flux_analyzer import FluxAnalyzer
from poster_manager import PosterManager
from source_material_analyzer import SourceMaterialAnalyzer
from deepseek_analyzer import DeepSeekAnalyzer
from perplexity_analyzer import PerplexityAnalyzer
from pdf_processor import PDFProcessor
from cost_tracker import CostTracker
from budget_utils import estimate_budget_from_screenplay, categorize_budget
from incentive_models import IncentiveDatabase, FilmIncentive, find_best_incentives_for_budget, get_incentives_by_analysis
from pydantic import BaseModel

load_dotenv(dotenv_path='../.env')
POSTER_GENERATION_ENABLED = os.getenv("POSTER_GENERATION_ENABLED", "true").lower() == "true"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request queuing system
MAX_CONCURRENT_ANALYSES = 3  # Limit concurrent analyses
analysis_semaphore = asyncio.Semaphore(MAX_CONCURRENT_ANALYSES)
analysis_queue_size = 0

# Initialize FastAPI app
app = FastAPI(
    title="Quilty Screenplay Analysis Service",
    description="Advanced screenplay analysis platform",
    version="1.0.0"
)

# Enable CORS for SvelteKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174", 
        "https://devtask.online",
        "http://devtask.online"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    db = ScreenplayDatabase()
    claude_analyzer = ClaudeOpusAnalyzer()
    grok_analyzer = GrokAnalyzer()
    openai_analyzer = OpenAIAnalyzer()
    gpt5_analyzer = GPT5Analyzer()
    # piapi_analyzer = PiAPIAnalyzer()  # Commented out - not working
    flux_analyzer = FluxAnalyzer()
    poster_manager = PosterManager() if POSTER_GENERATION_ENABLED else None
    source_material_analyzer = SourceMaterialAnalyzer()
    deepseek_analyzer = DeepSeekAnalyzer()
    perplexity_analyzer = PerplexityAnalyzer()
    pdf_processor = PDFProcessor()
    cost_tracker = CostTracker()
    incentive_db = IncentiveDatabase()
    logger.info("✅ All analysis engines initialized successfully")
    
    # Progress tracking store
    progress_store: Dict[str, Dict[str, Any]] = {}
except Exception as e:
    logger.error(f"❌ Service initialization failed: {e}")
    raise

# Progress tracking functions
def update_progress(analysis_id: str, stage: str, progress: int, message: str, details: Optional[Dict] = None):
    """Update progress for an analysis"""
    progress_store[analysis_id] = {
        'stage': stage,
        'progress': progress,
        'message': message,
        'details': details or {},
        'timestamp': time.time()
    }
    logger.info(f"📊 Progress {analysis_id}: {stage} ({progress}%) - {message}")

def get_progress(analysis_id: str) -> Dict[str, Any]:
    """Get current progress for an analysis"""
    return progress_store.get(analysis_id, {
        'stage': 'unknown',
        'progress': 0,
        'message': 'Analysis not found',
        'details': {},
        'timestamp': time.time()
    })

async def progress_stream(analysis_id: str) -> AsyncGenerator[str, None]:
    """Stream progress updates for an analysis with improved error handling"""
    last_update = 0
    timeout_count = 0
    max_timeout = 600  # 10 minutes timeout (increased for long analyses)
    heartbeat_interval = 5  # Send heartbeat every 5 seconds
    
    logger.info(f"📊 Starting progress stream for analysis: {analysis_id}")
    
    try:
        # Send initial connection confirmation
        yield f"data: {json.dumps({'heartbeat': True, 'connected': True, 'timestamp': time.time()})}\n\n"
        
        while timeout_count < max_timeout:
            try:
                current_progress = get_progress(analysis_id)
                current_time = current_progress.get('timestamp', 0)
                
                # Send update if there's new progress
                if current_time > last_update:
                    data = json.dumps(current_progress)
                    yield f"data: {data}\n\n"
                    last_update = current_time
                    timeout_count = 0
                    
                    logger.debug(f"📊 Progress update sent for {analysis_id}: {current_progress.get('stage', 'unknown')} ({current_progress.get('progress', 0)}%)")
                    
                    # Check if analysis is complete or errored
                    if current_progress.get('progress', 0) >= 100 or current_progress.get('stage') in ['complete', 'error']:
                        logger.info(f"✅ Analysis stream completed for {analysis_id}")
                        break
                else:
                    # Send heartbeat every 5 seconds
                    if timeout_count % heartbeat_interval == 0:
                        yield f"data: {json.dumps({'heartbeat': True, 'timestamp': time.time()})}\n\n"
                    timeout_count += 1
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error in progress stream for {analysis_id}: {e}")
                # Send error to client but continue trying
                error_data = json.dumps({
                    'stage': 'error',
                    'progress': 0,
                    'message': f'Streaming error: {str(e)}',
                    'timestamp': time.time()
                })
                yield f"data: {error_data}\n\n"
                await asyncio.sleep(5)  # Wait longer on errors
                
    except Exception as e:
        logger.error(f"❌ Critical error in progress stream for {analysis_id}: {e}")
        # Send final error message
        error_data = json.dumps({
            'stage': 'error', 
            'progress': 0, 
            'message': f'Stream failed: {str(e)}',
            'timestamp': time.time()
        })
        yield f"data: {error_data}\n\n"
    finally:
        # Send final completion message
        logger.info(f"🔚 Progress stream ended for {analysis_id}")
        yield f"data: {json.dumps({'stage': 'stream_ended', 'progress': 100, 'message': 'Stream ended', 'timestamp': time.time()})}\n\n"

# Request/Response Models
class AnalysisRequest(BaseModel):
    title: str
    screenplay_text: str
    genre: Optional[str] = None
    user_id: str
    budget_estimate: Optional[float] = None
    
    @field_validator('budget_estimate')
    @classmethod
    def validate_budget(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Budget must be non-negative')
            if v > 1_000_000_000:
                raise ValueError('Budget cannot exceed $1 billion')
            if v > 0 and v < 1000:
                raise ValueError('Budget must be at least $1,000 for professional analysis')
        return v

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str

class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Quilty Screenplay Analysis Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Text analysis endpoint
@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze screenplay from text input"""
    
    logger.info(f"📝 Text analysis request: {request.title} (user: {request.user_id})")
    
    try:
        # Generate analysis ID
        analysis_id = f"text_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Create initial database record
        initial_data = {
            'id': analysis_id,
            'user_id': request.user_id,
            'title': request.title,
            'genre': request.genre,
            'user_proposed_budget': request.budget_estimate,
            'status': 'processing',
            'ai_model': 'Claude Opus 4.1',
            'original_filename': None,
            'file_path': None,
            'file_size': len(request.screenplay_text),
            'detected_genre': None,
            'subgenre': None,
            'overall_score': None,
            'recommendation': None,
            'one_line_verdict': None,
            'logline': None,
            'executive_summary': None,
            'structural_analysis': None,
            'character_analysis': None,
            'thematic_depth': None,
            'craft_evaluation': None,
            'genre_mastery': None,
            'top_strengths': None,
            'key_weaknesses': None,
            'suggestions': None,
            'improvement_strategies': None,
            'commercial_viability': None,
            'target_audience': None,
            'comparable_films': None,
            'casting_suggestions': None,
            'casting_vision': None,
            'director_recommendation': None,
            'grok_score': None,
            'grok_recommendation': None,
            'grok_verdict': None,
            'grok_confidence': None,
            'grok_cultural_analysis': None,
            'grok_brutal_honesty': None,
            'grok_controversy_analysis': None,
            'grok_movie_poster_url': None,
            'grok_poster_prompt': None,
            'openai_score': None,
            'openai_recommendation': None,
            'openai_verdict': None,
            'piapi_poster_url': None,
            'piapi_poster_prompt': None,
            'piapi_poster_cost': None,
            'piapi_poster_success': None,
            'piapi_poster_error': None,
            'confidence_level': None,
            'processing_time': None,
            'cost': None,
            'raw_api_request': None,
            'raw_api_response': None
        }
        
        if not db.insert_initial_analysis(initial_data):
            raise HTTPException(status_code=500, detail="Failed to create analysis record")
        
        # Start queued background analysis
        background_tasks.add_task(
            queued_analysis,
            process_text_analysis,
            analysis_id,
            request.screenplay_text,
            request.title,
            request.genre,
            request.user_id,
            request.budget_estimate
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            message="Analysis started successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Text analysis request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PDF upload and analysis endpoint
@app.post("/analyze/pdf", response_model=AnalysisResponse)
async def analyze_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    genre: Optional[str] = Form(None),
    user_id: str = Form(...),
    budget_estimate: Optional[float] = Form(None)
):
    """Upload and analyze PDF screenplay with optional budget estimate"""
    
    # Validate budget estimate
    if budget_estimate is not None:
        if budget_estimate < 0:
            raise HTTPException(status_code=400, detail="Budget must be non-negative")
        if budget_estimate > 1_000_000_000:
            raise HTTPException(status_code=400, detail="Budget cannot exceed $1 billion")
        if budget_estimate > 0 and budget_estimate < 1000:
            raise HTTPException(status_code=400, detail="Budget must be at least $1,000 for professional analysis")
    
    logger.info(f"📄 PDF analysis request: {title} (file: {file.filename}, user: {user_id})")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size (50MB limit)
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Generate analysis ID
        analysis_id = f"pdf_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Save uploaded file
        file_path = pdf_processor.save_uploaded_file(file_content, file.filename, user_id)
        
        # Create initial database record
        initial_data = {
            'id': analysis_id,
            'user_id': user_id,
            'title': title,
            'genre': genre,
            'user_proposed_budget': budget_estimate,
            'status': 'processing',
            'ai_model': 'Claude Opus 4.1',
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'detected_genre': None,
            'subgenre': None,
            'overall_score': None,
            'recommendation': None,
            'one_line_verdict': None,
            'logline': None,
            'executive_summary': None,
            'structural_analysis': None,
            'character_analysis': None,
            'thematic_depth': None,
            'craft_evaluation': None,
            'genre_mastery': None,
            'top_strengths': None,
            'key_weaknesses': None,
            'suggestions': None,
            'improvement_strategies': None,
            'commercial_viability': None,
            'target_audience': None,
            'comparable_films': None,
            'casting_suggestions': None,
            'casting_vision': None,
            'director_recommendation': None,
            'grok_score': None,
            'grok_recommendation': None,
            'grok_verdict': None,
            'grok_confidence': None,
            'grok_cultural_analysis': None,
            'grok_brutal_honesty': None,
            'grok_controversy_analysis': None,
            'grok_movie_poster_url': None,
            'grok_poster_prompt': None,
            'grok_raw_response': None,
            'openai_score': None,
            'openai_recommendation': None,
            'openai_verdict': None,
            'openai_confidence': None,
            'openai_commercial_assessment': None,
            'openai_technical_craft': None,
            'openai_industry_comparison': None,
            'openai_raw_response': None,
            'openai_movie_poster_url': None,
            'openai_poster_prompt': None,
            'confidence_level': None,
            'processing_time': None,
            'cost': None,
            'raw_api_request': None,
            'raw_api_response': None
        }
        
        if not db.insert_initial_analysis(initial_data):
            raise HTTPException(status_code=500, detail="Failed to create analysis record")
        
        # Start queued background analysis
        background_tasks.add_task(
            queued_analysis,
            process_pdf_analysis,
            analysis_id,
            file_content,
            file.filename,
            title,
            genre,
            user_id,
            budget_estimate
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            message="PDF upload and analysis started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF analysis request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis status and results
@app.get("/analysis/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis(analysis_id: str):
    """Get analysis status and results"""
    
    try:
        analysis = db.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Convert datetime objects to strings for JSON serialization
        if analysis.get('created_at'):
            analysis['created_at'] = analysis['created_at'].isoformat()
        if analysis.get('updated_at'):
            analysis['updated_at'] = analysis['updated_at'].isoformat()
        
        return AnalysisStatusResponse(
            analysis_id=analysis_id,
            status=analysis['status'],
            result=analysis if analysis['status'] == 'completed' else None,
            error_message=analysis.get('error_message')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get user's analyses
@app.get("/user/{user_id}/analyses")
async def get_user_analyses(user_id: str, limit: int = 50, offset: int = 0):
    """Get all analyses for a user"""
    
    try:
        analyses = db.get_user_analyses(user_id, limit, offset)
        
        # Convert datetime objects to strings
        for analysis in analyses:
            if analysis.get('created_at'):
                analysis['created_at'] = analysis['created_at'].isoformat()
            if analysis.get('updated_at'):
                analysis['updated_at'] = analysis['updated_at'].isoformat()
        
        return {
            "user_id": user_id,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting user analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get user usage statistics
@app.get("/user/{user_id}/usage")
async def get_user_usage(user_id: str):
    """Get user usage statistics and costs"""
    
    try:
        usage_stats = db.get_user_usage_stats(user_id)
        
        if not usage_stats:
            # Return default stats for new users
            usage_stats = {
                'user_id': user_id,
                'monthly_analyses_count': 0,
                'monthly_cost': 0.0,
                'monthly_tokens': 0,
                'total_analyses_count': 0,
                'total_cost': 0.0,
                'total_tokens': 0,
                'last_analysis_at': None
            }
        
        # Convert datetime to string if present
        if usage_stats.get('last_analysis_at'):
            usage_stats['last_analysis_at'] = usage_stats['last_analysis_at'].isoformat()
        if usage_stats.get('last_updated'):
            usage_stats['last_updated'] = usage_stats['last_updated'].isoformat()
        
        return usage_stats
        
    except Exception as e:
        logger.error(f"❌ Error getting user usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{analysis_id}/progress")
async def stream_progress(analysis_id: str):
    """Stream real-time progress updates for an analysis"""
    return StreamingResponse(
        progress_stream(analysis_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Queued analysis wrapper
async def queued_analysis(analysis_func, *args, **kwargs):
    """Wrapper to limit concurrent analyses using semaphore"""
    global analysis_queue_size
    
    analysis_queue_size += 1
    logger.info(f"📊 Analysis queued. Queue size: {analysis_queue_size}, Active: {MAX_CONCURRENT_ANALYSES - analysis_semaphore._value}")
    
    async with analysis_semaphore:
        try:
            analysis_queue_size -= 1
            logger.info(f"🚀 Starting analysis. Queue size: {analysis_queue_size}")
            await analysis_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Queued analysis failed: {e}")
            raise
        finally:
            logger.info(f"✅ Analysis completed. Available slots: {analysis_semaphore._value}")

# Background task functions
async def process_text_analysis(
    analysis_id: str,
    screenplay_text: str,
    title: str,
    genre: Optional[str],
    user_id: str,
    budget_estimate: Optional[float]
):
    """Background task to process text analysis"""
    
    logger.info(f"🔄 Processing text analysis: {analysis_id}")
    update_progress(analysis_id, "starting", 5, "Initializing text analysis...")
    
    # Initialize variables
    source_result = None
    
    try:
        # Start source material analysis (early - informs other analyses)
        update_progress(analysis_id, "source_analysis", 15, "Analyzing source material and IP...", {
            "model": "gpt-4o",
            "estimated_time": "10-15 seconds"
        })
        source_result = await source_material_analyzer.analyze_source_material(
            screenplay_text=screenplay_text,
            title=title
        )
        if source_result and source_result.success:
            update_progress(analysis_id, "source_complete", 20, f"Source material analysis complete!", {
                "has_source_material": source_result.has_source_material,
                "source_type": source_result.source_type,
                "source_title": source_result.source_title,
                "cost": f"${source_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "source_skipped", 20, "Source material analysis skipped (API unavailable)")

        # Estimate budget if not provided by user
        ai_budget_min, ai_budget_optimal, ai_budget_max, budget_notes = None, None, None, None
        budget_category = None
        
        if budget_estimate:
            # User provided budget - categorize it
            budget_category = categorize_budget(budget_estimate)
            budget_notes = {
                "type": "user_specified",
                "amount": budget_estimate,
                "category": budget_category,
                "note": f"User-specified budget: ${budget_estimate:,.0f} ({budget_category} tier)"
            }
        else:
            # AI estimate budget from screenplay content
            try:
                ai_budget_min, ai_budget_optimal, ai_budget_max, budget_reasoning = estimate_budget_from_screenplay(
                    screenplay_text, title, genre or "Drama"
                )
                budget_category = categorize_budget(ai_budget_optimal)
                budget_notes = {
                    "type": "ai_estimated",
                    "min_budget": ai_budget_min,
                    "optimal_budget": ai_budget_optimal,
                    "max_budget": ai_budget_max,
                    "category": budget_category,
                    "reasoning": budget_reasoning,
                    "note": f"AI estimated budget range. {budget_reasoning}"
                }
                
                update_progress(analysis_id, "budget_estimated", 22, f"Budget estimated: ${ai_budget_optimal:,.0f} ({budget_category})", {
                    "min_budget": f"${ai_budget_min:,.0f}",
                    "optimal_budget": f"${ai_budget_optimal:,.0f}",
                    "max_budget": f"${ai_budget_max:,.0f}",
                    "category": budget_category
                })
            except Exception as e:
                logger.warning(f"Budget estimation failed: {e}")
                budget_notes = {
                    "type": "unavailable",
                    "note": "Budget estimation unavailable",
                    "error": "Budget estimation failed"
                }

        # Start Claude analysis (primary - needed for genre detection)
        update_progress(analysis_id, "claude_analysis", 25, "Starting Claude Opus 4.1 analysis...", {
            "model": "claude-opus-4-1-20250805",
            "text_length": len(screenplay_text),
            "estimated_time": "60-90 seconds"
        })
        result = await claude_analyzer.analyze_screenplay(
            screenplay_text=screenplay_text,
            title=title,
            genre=genre,
            user_id=user_id,
            budget_estimate=budget_estimate
        )
        if result:
            update_progress(analysis_id, "claude_complete", 50, f"Craft analysis complete! Score: {result.overall_score}/10", {
                "score": result.overall_score,
                "recommendation": result.recommendation,
                "cost": f"${result.cost:.4f}"
            })
        
        # Run all secondary analyses in parallel (much faster!)
        update_progress(analysis_id, "parallel_analysis", 55, "Running parallel AI analysis & producer intelligence...", {
            "models": "Grok 4, OpenAI ChatGPT-5, GPT-5 Writing Excellence, DeepSeek Financial, Perplexity Market Research, PiAPI",
            "estimated_time": "60-90 seconds"
        })
        
        # Create parallel tasks
        tasks = []
        
        # Grok analysis task
        tasks.append(grok_analyzer.analyze(
            screenplay_text=screenplay_text,
            title=title,
            genre=genre or result.genre,
            budget_estimate=budget_estimate
        ))
        
        # OpenAI analysis task
        tasks.append(openai_analyzer.analyze(
            screenplay_text=screenplay_text,
            title=title,
            genre=genre or result.genre,
            budget_estimate=budget_estimate
        ))
        
        # GPT-5 Writing Excellence analysis task
        tasks.append(gpt5_analyzer.analyze(
            screenplay_text=screenplay_text,
            title=title,
            genre=genre or result.genre,
            budget_estimate=budget_estimate
        ))
        
        # DeepSeek financial analysis task
        tasks.append(deepseek_analyzer.analyze_financial_potential(
            screenplay_text=screenplay_text,
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            budget_estimate=budget_estimate,
            comparable_films=[]    # Could be derived from Claude analysis
        ))
        
        # Perplexity market research task
        tasks.append(perplexity_analyzer.research_market_intelligence(
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            release_timeframe="next_12_months",
            budget_range=None,     # Could be estimated based on genre
            target_audience=None   # Could be derived from analysis
        ))
        
        # Enhanced poster collection generation task (feature-flagged)
        if POSTER_GENERATION_ENABLED and poster_manager is not None:
            tasks.append(poster_manager.generate_poster_collection(
                title=title,
                genre=genre or (result.genre if result else "Drama"),
                analysis_data={
                    'score': result.overall_score if result else 7.0,
                    'recommendation': result.recommendation if result else "Consider",
                    'themes': getattr(result, 'themes', []) if result else [],
                    'tone': getattr(result, 'tone', 'dramatic') if result else 'dramatic',
                    'main_characters': getattr(result, 'main_characters', []) if result else []
                },
                variations=['theatrical', 'character']  # Generate 2 main variations
            ))
        
        # Execute all tasks in parallel
        logger.info(f"🔧 Executing {len(tasks)} parallel tasks...")
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"🔧 Parallel results count: {len(parallel_results)}")
        if POSTER_GENERATION_ENABLED and poster_manager is not None:
            grok_result, openai_result, gpt5_result, deepseek_result, perplexity_result, poster_collection = parallel_results
        else:
            grok_result, openai_result, gpt5_result, deepseek_result, perplexity_result = parallel_results
            poster_collection = None
        logger.info(f"🔧 Poster collection type: {type(poster_collection)}")
        logger.info(f"🔧 Poster collection is Exception: {isinstance(poster_collection, Exception)}")
        if hasattr(poster_collection, 'success_count'):
            logger.info(f"🔧 Poster collection success count: {poster_collection.success_count}")
        
        # Handle Grok result
        if isinstance(grok_result, Exception):
            logger.error(f"Reality check analysis failed: {grok_result}")
            grok_result = None
        elif grok_result:
            update_progress(analysis_id, "grok_complete", 70, f"Reality check complete! Score: {grok_result.score}/10", {
                "score": grok_result.score,
                "recommendation": grok_result.recommendation,
                "cost": f"${grok_result.cost:.4f}"
            })
        
        # Handle OpenAI result
        if isinstance(openai_result, Exception):
            logger.error(f"Commercial analysis failed: {openai_result}")
            openai_result = None
        elif openai_result:
            update_progress(analysis_id, "openai_complete", 75, f"Commercial analysis complete! Score: {openai_result.score}/10", {
                "score": openai_result.score,
                "recommendation": openai_result.recommendation,
                "cost": f"${openai_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "openai_skipped", 75, "Commercial analysis skipped (service unavailable)")
        
        # Handle GPT-5 result
        if isinstance(gpt5_result, Exception):
            logger.error(f"Excellence analysis failed: {gpt5_result}")
            gpt5_result = None
        elif gpt5_result:
            update_progress(analysis_id, "gpt5_complete", 80, f"GPT-5 Writing Excellence complete! Score: {gpt5_result.score}/10", {
                "score": gpt5_result.score,
                "recommendation": gpt5_result.recommendation,
                "reasoning_depth": gpt5_result.reasoning_depth,
                "cost": f"${gpt5_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "gpt5_skipped", 80, "Excellence analysis skipped (service unavailable)")
        
        # Handle DeepSeek result
        if isinstance(deepseek_result, Exception):
            logger.error(f"DeepSeek analysis failed: {deepseek_result}")
            deepseek_result = None
        elif deepseek_result:
            update_progress(analysis_id, "deepseek_complete", 82, f"Financial analysis complete! Score: {deepseek_result.overall_financial_score}/10", {
                "financial_score": deepseek_result.overall_financial_score,
                "recommendation": deepseek_result.recommendation,
                "cost": f"${deepseek_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "deepseek_skipped", 82, "DeepSeek analysis skipped (API unavailable)")
        
        # Handle Perplexity result
        if isinstance(perplexity_result, Exception):
            logger.error(f"Perplexity research failed: {perplexity_result}")
            perplexity_result = None
        elif perplexity_result:
            update_progress(analysis_id, "perplexity_complete", 84, f"Market research complete! Score: {perplexity_result.market_opportunity_score}/10", {
                "market_score": perplexity_result.market_opportunity_score,
                "recommendation": perplexity_result.market_recommendation,
                "cost": f"${perplexity_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "perplexity_skipped", 84, "Perplexity research skipped (API unavailable)")
        
        # Handle Poster Collection result
        if isinstance(poster_collection, Exception):
            logger.error(f"Poster collection generation failed: {poster_collection}")
            poster_collection = None
        elif poster_collection and poster_collection.success_count > 0:
            update_progress(analysis_id, "posters_complete", 85, f"Generated {poster_collection.success_count} movie posters!", {
                "success_count": poster_collection.success_count,
                "best_poster_url": poster_collection.best_poster_url,
                "best_source": poster_collection.best_poster_source,
                "total_cost": f"${poster_collection.total_cost:.4f}"
            })
        else:
            reason = "Poster generation disabled" if not (POSTER_GENERATION_ENABLED and poster_manager is not None) else "Poster generation skipped (no APIs available)"
            update_progress(analysis_id, "posters_skipped", 85, reason)
        
        # Convert to database format
        update_progress(analysis_id, "saving", 92, "Saving analysis results to database...")
        db_data = claude_analyzer.to_database_format(result)
        
        # Add Grok results if available
        if grok_result:
            grok_data = grok_analyzer.to_database_format(grok_result)
            db_data.update(grok_data)
        
        # Add OpenAI results if available
        if openai_result:
            openai_data = openai_analyzer.to_database_format(openai_result)
            db_data.update(openai_data)
        
        # Add GPT-5 results if available
        if gpt5_result:
            gpt5_data = gpt5_analyzer.to_database_format(gpt5_result)
            db_data.update(gpt5_data)
        
        # Add DeepSeek results if available
        if deepseek_result:
            deepseek_data = deepseek_analyzer.to_database_format(deepseek_result)
            db_data.update(deepseek_data)
        
        # Add Perplexity results if available
        if perplexity_result:
            perplexity_data = perplexity_analyzer.to_database_format(perplexity_result)
            db_data.update(perplexity_data)
        
        # Add Poster Collection results if available
        if poster_collection:
            poster_data = poster_manager.to_database_format(poster_collection)
            logger.info(f"🎨 Poster collection database data: {list(poster_data.keys())}")
            logger.info(f"🎨 Poster success count: {poster_data.get('poster_success_count', 'MISSING')}")
            logger.info(f"🎨 Poster best URL: {poster_data.get('poster_best_url', 'MISSING')[:100] if poster_data.get('poster_best_url') else 'MISSING'}...")
            db_data.update(poster_data)
        else:
            logger.warning(f"⚠️ No poster collection data to save")
        
        # Add Source Material results if available
        if source_result:
            source_data = source_material_analyzer.to_database_format(source_result)
            db_data.update(source_data)
        
        db_data.update({
            'id': analysis_id,
            'user_id': user_id,
            'original_filename': None,
            'file_path': None,
            'file_size': len(screenplay_text),
            # Budget information
            'budget_category': budget_category,
            'ai_budget_min': ai_budget_min,
            'ai_budget_optimal': ai_budget_optimal,
            'ai_budget_max': ai_budget_max,
            'budget_notes': budget_notes
        })
        
        # Update database record
        logger.info(f"🔍 Saving analysis data: {list(db_data.keys())}")
        
        # Ensure all dict values are properly JSON serialized
        import json
        for key, value in db_data.items():
            if isinstance(value, dict):
                db_data[key] = json.dumps(value)
            elif isinstance(value, list):
                db_data[key] = json.dumps(value)
        
        if db.save_analysis(db_data):
            total_cost = result.cost + (grok_result.cost if grok_result else 0) + (openai_result.cost if openai_result else 0) + (gpt5_result.cost if gpt5_result else 0) + (deepseek_result.cost if deepseek_result else 0) + (perplexity_result.cost if perplexity_result else 0) + (poster_collection.total_cost if poster_collection else 0) + (source_result.cost if source_result else 0)
            update_progress(analysis_id, "complete", 100, "Analysis complete! Results saved successfully.", {
                "claude_score": result.overall_score,
                "grok_score": grok_result.score if grok_result else None,
                "openai_score": openai_result.score if openai_result else None,
                "gpt5_score": gpt5_result.score if gpt5_result else None,
                "deepseek_score": deepseek_result.overall_financial_score if deepseek_result else None,
                "perplexity_score": perplexity_result.market_opportunity_score if perplexity_result else None,
                "total_cost": f"${total_cost:.4f}"
            })
            logger.info(f"✅ Text analysis completed: {analysis_id}")
            
            # Track API usage for all providers
            cost_tracker.track_usage(
                user_id=user_id,
                analysis_id=analysis_id,
                api_provider="anthropic",
                model_name="claude-opus-4-1-20250805",
                cost=result.cost,
                processing_time=result.processing_time,
                success=True
            )
            
            if grok_result:
                cost_tracker.track_usage(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    api_provider="xai",
                    model_name="grok-4-latest",
                    cost=grok_result.cost,
                    processing_time=grok_result.processing_time,
                    success=True
                )
            
            if openai_result:
                cost_tracker.track_usage(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    api_provider="openai",
                    model_name="gpt-5",
                    cost=openai_result.cost,
                    processing_time=openai_result.processing_time,
                    success=True
                )
        else:
            raise Exception("Failed to save analysis results")
            
    except Exception as e:
        logger.error(f"❌ Text analysis failed: {analysis_id} - {e}")
        update_progress(analysis_id, "error", 0, f"Analysis failed: {str(e)}", {"error": str(e)})
        db.update_analysis_status(analysis_id, 'error', str(e))
        
        # Track failed usage
        cost_tracker.track_usage(
            user_id=user_id,
            analysis_id=analysis_id,
            api_provider="anthropic",
            model_name="claude-opus-4-1-20250805",
            cost=0.0,
            processing_time=0.0,
            success=False,
            error_message=str(e)
        )

async def process_pdf_analysis(
    analysis_id: str,
    file_content: bytes,
    filename: str,
    title: str,
    genre: Optional[str],
    user_id: str,
    budget_estimate: Optional[float]
):
    """Background task to process PDF analysis"""
    
    logger.info(f"🔄 Processing PDF analysis: {analysis_id}")
    update_progress(analysis_id, "starting", 5, "Initializing PDF analysis...")
    
    # Initialize variables
    source_result = None
    
    try:
        # Extract text from PDF
        update_progress(analysis_id, "pdf_processing", 10, "Extracting text from PDF...")
        pdf_result = await pdf_processor.process_pdf(file_content, filename)
        
        if not pdf_result.success:
            raise Exception(f"PDF processing failed: {pdf_result.error_message}")
        
        logger.info(f"📖 PDF text extracted: {len(pdf_result.extracted_text):,} characters")
        update_progress(analysis_id, "pdf_complete", 20, f"PDF processed: {len(pdf_result.extracted_text):,} characters extracted")
        
        # Start source material analysis (early - informs other analyses)
        update_progress(analysis_id, "source_analysis", 20, "Analyzing source material and IP...", {
            "model": "gpt-4o",
            "estimated_time": "10-15 seconds"
        })
        source_result = await source_material_analyzer.analyze_source_material(
            screenplay_text=pdf_result.extracted_text,
            title=title
        )
        if source_result and source_result.success:
            update_progress(analysis_id, "source_complete", 25, f"Source material analysis complete!", {
                "has_source_material": source_result.has_source_material,
                "source_type": source_result.source_type,
                "source_title": source_result.source_title,
                "cost": f"${source_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "source_skipped", 25, "Source material analysis skipped (API unavailable)")

        # Estimate budget if not provided by user (PDF version)
        ai_budget_min, ai_budget_optimal, ai_budget_max, budget_notes = None, None, None, None
        budget_category = None
        
        if budget_estimate:
            # User provided budget - categorize it
            budget_category = categorize_budget(budget_estimate)
            budget_notes = {
                "type": "user_specified",
                "amount": budget_estimate,
                "category": budget_category,
                "note": f"User-specified budget: ${budget_estimate:,.0f} ({budget_category} tier)"
            }
        else:
            # AI estimate budget from screenplay content
            try:
                ai_budget_min, ai_budget_optimal, ai_budget_max, budget_reasoning = estimate_budget_from_screenplay(
                    pdf_result.extracted_text, title, genre or "Drama"
                )
                budget_category = categorize_budget(ai_budget_optimal)
                budget_notes = {
                    "type": "ai_estimated",
                    "min_budget": ai_budget_min,
                    "optimal_budget": ai_budget_optimal,
                    "max_budget": ai_budget_max,
                    "category": budget_category,
                    "reasoning": budget_reasoning,
                    "note": f"AI estimated budget range. {budget_reasoning}"
                }
                
                update_progress(analysis_id, "budget_estimated", 27, f"Budget estimated: ${ai_budget_optimal:,.0f} ({budget_category})", {
                    "min_budget": f"${ai_budget_min:,.0f}",
                    "optimal_budget": f"${ai_budget_optimal:,.0f}",
                    "max_budget": f"${ai_budget_max:,.0f}",
                    "category": budget_category
                })
            except Exception as e:
                logger.warning(f"Budget estimation failed: {e}")
                budget_notes = {
                    "type": "unavailable",
                    "note": "Budget estimation unavailable",
                    "error": "Budget estimation failed"
                }

        # Start Claude analysis (primary - with built-in retry for 529 errors)
        result = None
        primary_analysis_cost = 0.0
        claude_failed = False
        
        try:
            update_progress(analysis_id, "claude_analysis", 30, "Starting craft analysis...", {
                "model": "claude-opus-4-1-20250805",
                "estimated_time": "60-90 seconds (with retries if overloaded)"
            })
            result = await claude_analyzer.analyze_screenplay(
                screenplay_text=pdf_result.extracted_text,
                title=title,
                genre=genre,
                user_id=user_id,
                budget_estimate=budget_estimate
            )
            primary_analysis_cost = result.cost
            
        except Exception as claude_error:
            error_str = str(claude_error)
            claude_failed = True
            
            # Log Claude failure but continue with other services
            if "overloaded" in error_str.lower() or "529" in error_str:
                logger.warning(f"⚠️ Claude analysis failed after retries (overloaded): {claude_error}")
                update_progress(analysis_id, "claude_failed", 35, "Claude analysis failed (overloaded after retries) - continuing with other AI services...", {
                    "claude_error": "API overloaded after multiple retries",
                    "continuing": "Will proceed with Grok, OpenAI, GPT-5, etc."
                })
            else:
                logger.warning(f"⚠️ Claude analysis failed: {claude_error}")
                update_progress(analysis_id, "claude_failed", 35, "Claude analysis failed - continuing with other AI services...", {
                    "claude_error": str(claude_error),
                    "continuing": "Will proceed with Grok, OpenAI, GPT-5, etc."
                })
        
        # If Claude succeeded, show success message
        if result and not claude_failed:
            update_progress(analysis_id, "claude_complete", 45, f"Craft analysis complete! Score: {result.overall_score}/10", {
                "score": result.overall_score,
                "recommendation": result.recommendation,
                "cost": f"${result.cost:.4f}"
            })
        else:
            # Claude failed, we'll rely on other AI services for the main analysis
            # Set a default genre for other services if not provided
            if not genre:
                genre = "Drama"  # Default genre when Claude can't detect it
        
        # Run all secondary analyses in parallel (much faster!)
        update_progress(analysis_id, "parallel_analysis", 50, "Running parallel analysis & poster generation...", {
            "models": "Grok 4, OpenAI ChatGPT-5, GPT-5 Writing Excellence, PiAPI",
            "estimated_time": "45-60 seconds"
        })
        
        # Create parallel tasks
        tasks = []
        
        # Grok analysis task
        tasks.append(grok_analyzer.analyze(
            screenplay_text=pdf_result.extracted_text,
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            budget_estimate=budget_estimate
        ))
        
        # OpenAI analysis task
        tasks.append(openai_analyzer.analyze(
            screenplay_text=pdf_result.extracted_text,
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            budget_estimate=budget_estimate
        ))
        
        # GPT-5 Writing Excellence analysis task
        tasks.append(gpt5_analyzer.analyze(
            screenplay_text=pdf_result.extracted_text,
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            budget_estimate=budget_estimate
        ))
        
        # DeepSeek financial analysis task (enhanced with incentive data)
        tasks.append(deepseek_analyzer.analyze_financial_potential(
            screenplay_text=pdf_result.extracted_text,
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            budget_estimate=budget_estimate,
            comparable_films=[],    # Could be derived from Claude analysis
            include_incentive_analysis=True  # Enable incentive integration
        ))
        
        # Perplexity market research task
        tasks.append(perplexity_analyzer.research_market_intelligence(
            title=title,
            genre=genre or (result.genre if result else "Drama"),
            release_timeframe="next_12_months",
            budget_range=None,
            target_audience=getattr(result, 'target_audience', 'General audiences') if result else 'General audiences'
        ))
        
        # Enhanced poster collection generation task (feature-flagged)
        if POSTER_GENERATION_ENABLED and poster_manager is not None:
            tasks.append(poster_manager.generate_poster_collection(
                title=title,
                genre=genre or (result.genre if result else "Drama"),
                analysis_data={
                    'score': result.overall_score if result else 7.0,
                    'recommendation': result.recommendation if result else "Consider",
                    'themes': getattr(result, 'themes', []) if result else [],
                    'tone': getattr(result, 'tone', 'dramatic') if result else 'dramatic',
                    'main_characters': getattr(result, 'main_characters', []) if result else []
                },
                variations=['theatrical', 'character']  # Generate 2 main variations
            ))
        
        # Execute all tasks in parallel
        logger.info(f"🔧 Executing {len(tasks)} parallel tasks...")
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"🔧 Parallel results count: {len(parallel_results)}")
        if POSTER_GENERATION_ENABLED and poster_manager is not None:
            grok_result, openai_result, gpt5_result, deepseek_result, perplexity_result, poster_collection = parallel_results
        else:
            grok_result, openai_result, gpt5_result, deepseek_result, perplexity_result = parallel_results
            poster_collection = None
        logger.info(f"🔧 Poster collection type: {type(poster_collection)}")
        logger.info(f"🔧 Poster collection is Exception: {isinstance(poster_collection, Exception)}")
        if hasattr(poster_collection, 'success_count'):
            logger.info(f"🔧 Poster collection success count: {poster_collection.success_count}")
        
        # Handle Grok result
        if isinstance(grok_result, Exception):
            logger.error(f"Reality check analysis failed: {grok_result}")
            grok_result = None
        elif grok_result:
            update_progress(analysis_id, "grok_complete", 70, f"Reality check complete! Score: {grok_result.score}/10", {
                "score": grok_result.score,
                "recommendation": grok_result.recommendation,
                "cost": f"${grok_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "grok_skipped", 70, "Reality check skipped (service unavailable)")
        
        # Handle OpenAI result
        if isinstance(openai_result, Exception):
            logger.error(f"Commercial analysis failed: {openai_result}")
            openai_result = None
        elif openai_result:
            update_progress(analysis_id, "openai_complete", 75, f"Commercial analysis complete! Score: {openai_result.score}/10", {
                "score": openai_result.score,
                "recommendation": openai_result.recommendation,
                "cost": f"${openai_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "openai_skipped", 75, "Commercial analysis skipped (service unavailable)")
        
        # Handle GPT-5 result
        if isinstance(gpt5_result, Exception):
            logger.error(f"Excellence analysis failed: {gpt5_result}")
            gpt5_result = None
        elif gpt5_result:
            update_progress(analysis_id, "gpt5_complete", 78, f"Excellence analysis complete! Score: {gpt5_result.score}/10", {
                "score": gpt5_result.score,
                "recommendation": gpt5_result.recommendation,
                "reasoning_depth": gpt5_result.reasoning_depth,
                "cost": f"${gpt5_result.cost:.4f}"
            })
        else:
            update_progress(analysis_id, "gpt5_skipped", 78, "GPT-5 analysis skipped (API unavailable)")
        
        # Handle Poster Collection result
        if isinstance(poster_collection, Exception):
            logger.error(f"Poster collection generation failed: {poster_collection}")
            poster_collection = None
        elif poster_collection and poster_collection.success_count > 0:
            update_progress(analysis_id, "posters_complete", 80, f"Generated {poster_collection.success_count} movie posters!", {
                "success_count": poster_collection.success_count,
                "best_poster_url": poster_collection.best_poster_url,
                "best_source": poster_collection.best_poster_source,
                "total_cost": f"${poster_collection.total_cost:.4f}"
            })
        else:
            reason = "Poster generation disabled" if not (POSTER_GENERATION_ENABLED and poster_manager is not None) else "Poster generation skipped (no APIs available)"
            update_progress(analysis_id, "posters_skipped", 80, reason)
        
        # Convert to database format
        update_progress(analysis_id, "saving", 90, "Saving analysis results to database...")
        db_data = claude_analyzer.to_database_format(result)
        
        # Add Grok results if available
        if grok_result:
            grok_data = grok_analyzer.to_database_format(grok_result)
            db_data.update(grok_data)
        
        # Add OpenAI results if available
        if openai_result:
            openai_data = openai_analyzer.to_database_format(openai_result)
            db_data.update(openai_data)
        
        # Add GPT-5 results if available
        if gpt5_result:
            gpt5_data = gpt5_analyzer.to_database_format(gpt5_result)
            db_data.update(gpt5_data)
        
        # Add DeepSeek results if available
        if deepseek_result:
            deepseek_data = deepseek_analyzer.to_database_format(deepseek_result)
            db_data.update(deepseek_data)
        
        # Add Perplexity results if available
        if perplexity_result:
            perplexity_data = perplexity_analyzer.to_database_format(perplexity_result)
            db_data.update(perplexity_data)
        
        # Add Poster Collection results if available
        if poster_collection:
            poster_data = poster_manager.to_database_format(poster_collection)
            logger.info(f"🎨 Poster collection database data: {list(poster_data.keys())}")
            logger.info(f"🎨 Poster success count: {poster_data.get('poster_success_count', 'MISSING')}")
            logger.info(f"🎨 Poster best URL: {poster_data.get('poster_best_url', 'MISSING')[:100] if poster_data.get('poster_best_url') else 'MISSING'}...")
            db_data.update(poster_data)
        else:
            logger.warning(f"⚠️ No poster collection data to save")
        
        # Add Source Material results if available
        if source_result:
            source_data = source_material_analyzer.to_database_format(source_result)
            db_data.update(source_data)
        
        db_data.update({
            'id': analysis_id,
            'user_id': user_id,
            'original_filename': filename,
            'file_path': f"uploads/{user_id}_{int(time.time())}_{filename}",
            'file_size': len(file_content),
            # Budget information
            'budget_category': budget_category,
            'ai_budget_min': ai_budget_min,
            'ai_budget_optimal': ai_budget_optimal,
            'ai_budget_max': ai_budget_max,
            'budget_notes': budget_notes
        })
        
        # Update database record
        # Ensure all dict values are properly JSON serialized
        import json
        for key, value in db_data.items():
            if isinstance(value, dict):
                db_data[key] = json.dumps(value)
            elif isinstance(value, list):
                db_data[key] = json.dumps(value)
        
        if db.save_analysis(db_data):
            total_cost = result.cost + (grok_result.cost if grok_result else 0) + (openai_result.cost if openai_result else 0) + (gpt5_result.cost if gpt5_result else 0) + (deepseek_result.cost if deepseek_result else 0) + (perplexity_result.cost if perplexity_result else 0) + (poster_collection.total_cost if poster_collection else 0) + (source_result.cost if source_result else 0)
            update_progress(analysis_id, "complete", 100, "Analysis complete! Results saved successfully.", {
                "claude_score": result.overall_score,
                "grok_score": grok_result.score if grok_result else None,
                "openai_score": openai_result.score if openai_result else None,
                "gpt5_score": gpt5_result.score if gpt5_result else None,
                "deepseek_score": deepseek_result.overall_financial_score if deepseek_result else None,
                "perplexity_score": perplexity_result.market_opportunity_score if perplexity_result else None,
                "total_cost": f"${total_cost:.4f}"
            })
            logger.info(f"✅ PDF analysis completed: {analysis_id}")
            
            # Track Claude API usage
            cost_tracker.track_usage(
                user_id=user_id,
                analysis_id=analysis_id,
                api_provider="anthropic",
                model_name="claude-opus-4-1-20250805",
                cost=result.cost,
                processing_time=result.processing_time,
                success=True
            )
            
            # Track Grok API usage if available
            if grok_result:
                cost_tracker.track_usage(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    api_provider="xai",
                    model_name="grok-4-latest",
                    cost=grok_result.cost,
                    processing_time=grok_result.processing_time,
                    success=True
                )
        else:
            raise Exception("Failed to save analysis results")
            
    except Exception as e:
        logger.error(f"❌ PDF analysis failed: {analysis_id} - {e}")
        update_progress(analysis_id, "error", 0, f"Analysis failed: {str(e)}", {"error": str(e)})
        db.update_analysis_status(analysis_id, 'error', str(e))
        
        # Track failed usage
        cost_tracker.track_usage(
            user_id=user_id,
            analysis_id=analysis_id,
            api_provider="anthropic",
            model_name="claude-opus-4-1-20250805",
            cost=0.0,
            processing_time=0.0,
            success=False,
            error_message=str(e)
        )

# ==================== FILM INCENTIVE & GRANTS API ENDPOINTS ====================

@app.get("/api/incentives")
async def get_all_incentives(active_only: bool = True):
    """Get all film incentives"""
    try:
        incentives = incentive_db.get_all_incentives(active_only=active_only)
        
        # Convert to dict format for JSON response
        incentive_list = []
        for incentive in incentives:
            incentive_dict = {
                'id': incentive.id,
                'country': incentive.country,
                'region': incentive.region,
                'incentive_type': incentive.incentive_type,
                'percentage': incentive.percentage,
                'max_credit': incentive.max_credit,
                'minimum_spend': incentive.minimum_spend,
                'maximum_spend': incentive.maximum_spend,
                'requirements': incentive.requirements,
                'processing_time_days': incentive.processing_time_days,
                'is_active': incentive.is_active
            }
            incentive_list.append(incentive_dict)
        
        logger.info(f"📋 Returned {len(incentive_list)} incentives (active_only={active_only})")
        
        return {
            "success": True,
            "incentives": incentive_list,
            "count": len(incentive_list)
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving incentives: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve incentives: {str(e)}")

@app.get("/api/incentives/country/{country}")
async def get_incentives_by_country(country: str):
    """Get incentives for a specific country"""
    try:
        incentives = incentive_db.get_incentives_by_country(country)
        
        # Convert to dict format
        incentive_list = []
        for incentive in incentives:
            incentive_dict = {
                'id': incentive.id,
                'country': incentive.country,
                'region': incentive.region,
                'incentive_type': incentive.incentive_type,
                'percentage': incentive.percentage,
                'max_credit': incentive.max_credit,
                'minimum_spend': incentive.minimum_spend,
                'maximum_spend': incentive.maximum_spend,
                'requirements': incentive.requirements,
                'processing_time_days': incentive.processing_time_days
            }
            incentive_list.append(incentive_dict)
        
        logger.info(f"🌍 Returned {len(incentive_list)} incentives for {country}")
        
        return {
            "success": True,
            "country": country,
            "incentives": incentive_list,
            "count": len(incentive_list)
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving incentives for {country}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve incentives for {country}: {str(e)}")

@app.get("/api/incentives/calculator")
async def incentive_calculator(budget: float, min_percentage: float = 15.0):
    """Calculate potential savings for a given budget"""
    try:
        if budget <= 0:
            raise HTTPException(status_code=400, detail="Budget must be greater than 0")
        
        if budget > 1_000_000_000:
            raise HTTPException(status_code=400, detail="Budget cannot exceed $1 billion")
        
        # Find best incentives for this budget
        savings_data = find_best_incentives_for_budget(float(budget), limit=10)
        
        # Calculate summary statistics
        total_potential_savings = sum(float(item['final_savings']) for item in savings_data)
        best_savings = savings_data[0] if savings_data else None
        
        logger.info(f"💰 Calculated incentives for ${budget:,.0f} budget - found {len(savings_data)} options")
        
        return {
            "success": True,
            "budget": budget,
            "min_percentage": min_percentage,
            "savings_options": savings_data,
            "summary": {
                "total_options": len(savings_data),
                "best_savings": float(best_savings['final_savings']) if best_savings else 0,
                "best_location": f"{best_savings['country']}, {best_savings['region']}" if best_savings and best_savings['region'] else best_savings['country'] if best_savings else None,
                "total_potential_savings": total_potential_savings
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error calculating incentives: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate incentives: {str(e)}")

@app.get("/api/analysis/{analysis_id}/incentives")
async def get_analysis_incentives(analysis_id: str):
    """Get incentive analysis for a specific screenplay analysis"""
    try:
        # Get comprehensive incentive data for this analysis
        incentive_data = get_incentives_by_analysis(analysis_id)
        
        logger.info(f"📊 Retrieved incentive data for analysis {analysis_id}")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "incentive_data": incentive_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving incentives for analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve incentive data: {str(e)}")

# ==================== END INCENTIVE ENDPOINTS ====================

# ==================== SCREENPLAY ENDPOINTS ====================

@app.get("/api/screenplays/analyses")
async def get_all_analyses(user_id: str = "default"):
    """Get all screenplay analyses - compatibility endpoint for frontend"""
    try:
        # This endpoint provides the same functionality as /user/{user_id}/analyses
        # but with the URL structure the frontend expects
        return await get_user_analyses(user_id)
        
    except Exception as e:
        logger.error(f"❌ Error getting analyses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analyses: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Return basic dashboard stats
        total_analyses = len(await get_user_analyses("default"))
        
        return {
            "success": True,
            "stats": {
                "total_analyses": total_analyses,
                "analyses_this_month": total_analyses,  # Simplified for now
                "active_users": 1,
                "total_incentives": 15
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

# ==================== GRANTS & AWARDS API ENDPOINTS ====================

@app.get("/api/grants")
async def get_all_grants(active_only: bool = True, grant_type: Optional[str] = None):
    """Get all film grants and awards"""
    try:
        cursor = incentive_db.get_connection().cursor(dictionary=True)
        
        query = """
            SELECT id, name, organization, country, region, grant_type, 
                   amount_min, amount_max, eligibility_requirements, 
                   application_deadline, application_frequency, target_demographics,
                   genre_focus, website_url, success_rate_percentage, average_award_amount
            FROM film_grants_awards
        """
        
        conditions = []
        params = []
        
        if active_only:
            conditions.append("is_active = TRUE")
        
        if grant_type:
            conditions.append("grant_type = %s")
            params.append(grant_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY average_award_amount DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process results
        grants = []
        for row in results:
            # Parse JSON fields
            if row['eligibility_requirements']:
                try:
                    row['eligibility_requirements'] = json.loads(row['eligibility_requirements']) if isinstance(row['eligibility_requirements'], str) else row['eligibility_requirements']
                except (json.JSONDecodeError, TypeError):
                    row['eligibility_requirements'] = {}
            
            if row['target_demographics']:
                try:
                    row['target_demographics'] = json.loads(row['target_demographics']) if isinstance(row['target_demographics'], str) else row['target_demographics']
                except (json.JSONDecodeError, TypeError):
                    row['target_demographics'] = []
            
            if row['genre_focus']:
                try:
                    row['genre_focus'] = json.loads(row['genre_focus']) if isinstance(row['genre_focus'], str) else row['genre_focus']
                except (json.JSONDecodeError, TypeError):
                    row['genre_focus'] = []
            
            grants.append(row)
        
        logger.info(f"📋 Returned {len(grants)} grants (active_only={active_only}, type={grant_type})")
        
        return {
            "success": True,
            "grants": grants,
            "count": len(grants)
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving grants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve grants: {str(e)}")

@app.get("/api/grants/eligibility")
async def check_grant_eligibility(
    filmmaker_demographics: Optional[str] = None,
    project_genre: Optional[str] = None,
    project_stage: Optional[str] = None,
    budget_range: Optional[str] = None,
    location: Optional[str] = None
):
    """Check grant eligibility based on filmmaker and project criteria"""
    try:
        cursor = incentive_db.get_connection().cursor(dictionary=True)
        
        query = """
            SELECT id, name, organization, country, region, grant_type, 
                   amount_min, amount_max, eligibility_requirements, 
                   target_demographics, genre_focus, success_rate_percentage,
                   average_award_amount, application_deadline, website_url
            FROM film_grants_awards
            WHERE is_active = TRUE
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        eligible_grants = []
        
        for grant in results:
            eligibility_score = 0
            max_score = 0
            
            # Parse JSON fields
            target_demographics = []
            genre_focus = []
            requirements = {}
            
            try:
                if grant['target_demographics']:
                    target_demographics = json.loads(grant['target_demographics']) if isinstance(grant['target_demographics'], str) else grant['target_demographics']
                if grant['genre_focus']:
                    genre_focus = json.loads(grant['genre_focus']) if isinstance(grant['genre_focus'], str) else grant['genre_focus']
                if grant['eligibility_requirements']:
                    requirements = json.loads(grant['eligibility_requirements']) if isinstance(grant['eligibility_requirements'], str) else grant['eligibility_requirements']
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Check demographics match
            if filmmaker_demographics and target_demographics:
                max_score += 3
                if any(demo.lower() in filmmaker_demographics.lower() for demo in target_demographics):
                    eligibility_score += 3
            
            # Check genre match
            if project_genre and genre_focus:
                max_score += 2
                if any(genre.lower() in project_genre.lower() for genre in genre_focus):
                    eligibility_score += 2
            
            # Check location match
            if location:
                max_score += 1
                if location.lower() in grant['country'].lower() or (grant['region'] and location.lower() in grant['region'].lower()):
                    eligibility_score += 1
            
            # Calculate eligibility percentage
            eligibility_percentage = (eligibility_score / max_score * 100) if max_score > 0 else 50
            
            # Include grants with >30% match or no specific criteria
            if eligibility_percentage >= 30 or max_score == 0:
                grant['eligibility_score'] = eligibility_percentage
                grant['match_reasons'] = []
                
                if filmmaker_demographics and target_demographics:
                    matching_demos = [demo for demo in target_demographics if demo.lower() in filmmaker_demographics.lower()]
                    if matching_demos:
                        grant['match_reasons'].append(f"Demographics: {', '.join(matching_demos)}")
                
                if project_genre and genre_focus:
                    matching_genres = [genre for genre in genre_focus if genre.lower() in project_genre.lower()]
                    if matching_genres:
                        grant['match_reasons'].append(f"Genre: {', '.join(matching_genres)}")
                
                eligible_grants.append(grant)
        
        # Sort by eligibility score and average award amount
        eligible_grants.sort(key=lambda x: (x['eligibility_score'], x['average_award_amount'] or 0), reverse=True)
        
        return {
            "success": True,
            "eligible_grants": eligible_grants[:20],  # Top 20 matches
            "total_matches": len(eligible_grants),
            "criteria_used": {
                "filmmaker_demographics": filmmaker_demographics,
                "project_genre": project_genre,
                "project_stage": project_stage,
                "budget_range": budget_range,
                "location": location
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking grant eligibility: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check grant eligibility: {str(e)}")

# ==================== AUTH ENDPOINTS REMOVED ====================
# Auth is now handled by SvelteKit endpoints in src/routes/api/auth/
# This avoids conflicts between FastAPI and SvelteKit auth systems
# ==================== END AUTH ENDPOINTS ====================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8001
    port = int(os.getenv("SERVICE_PORT", 8001))
    
    logger.info(f"🚀 Starting Quilty Screenplay Analysis Service on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload to prevent constant crashes
        log_level="info"
    )
