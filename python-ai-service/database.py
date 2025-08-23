import os
import json
import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ScreenplayDatabase:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER") 
        self.password = os.getenv("DB_PASSWORD")
        # Fix password handling - remove quotes if present and handle $ characters properly
        if self.password:
            # Remove surrounding quotes if present
            if self.password.startswith('"') and self.password.endswith('"'):
                self.password = self.password[1:-1]
            elif self.password.startswith("'") and self.password.endswith("'"):
                self.password = self.password[1:-1]
            # Fix password escaping issue - remove extra backslash if present
            if '\\$' in self.password:
                self.password = self.password.replace('\\$', '$')
        self.database = os.getenv("DB_NAME")
        
        # Use connection pooling for better performance
        self.pool_config = {
            'pool_name': 'screenplay_pool',
            'pool_size': 10,
            'pool_reset_session': True,
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'autocommit': True,
            'charset': 'utf8mb4',
            'use_unicode': True
        }
        
        self.connection_pool = None
        self.connection = None
        self.connect()
        self.init_tables()
    
    def connect(self):
        """Establish database connection pool"""
        try:
            # PyMySQL doesn't have built-in pooling, use single connection
            self.connection_pool = None
            
            # Create direct connection with mysql.connector
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
                charset='utf8mb4'
            )
            logger.info("✅ Database connection successful")
        except Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection
    
    def init_tables(self):
        """Initialize screenplay analysis tables"""
        try:
            cursor = self.connection.cursor()
            
            # Create screenplay_analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenplay_analyses (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    original_filename VARCHAR(500),
                    file_path VARCHAR(1000),
                    file_size INT,
                    genre VARCHAR(100),
                    detected_genre VARCHAR(100),
                    subgenre VARCHAR(100),
                    
                    -- Analysis Results
                    overall_score DECIMAL(3,1),
                    recommendation ENUM('Pass', 'Consider', 'Recommend', 'Strong Recommend'),
                    one_line_verdict TEXT,
                    logline TEXT,
                    executive_summary TEXT,
                    top_strengths JSON,
                    key_weaknesses JSON,
                    suggestions JSON,
                    commercial_viability TEXT,
                    target_audience TEXT,
                    comparable_films JSON,
                    casting_suggestions JSON,
                    structural_analysis TEXT,
                    character_analysis TEXT,
                    thematic_depth TEXT,
                    craft_evaluation TEXT,
                    genre_mastery TEXT,
                    improvement_strategies JSON,
                    casting_vision JSON,
                    director_recommendation TEXT,
                    
                    -- Grok Analysis Results (Phase 1)
                    grok_score DECIMAL(3,1),
                    grok_recommendation VARCHAR(50),
                    grok_verdict TEXT,
                    grok_confidence DECIMAL(3,2),
                    grok_cultural_analysis JSON,
                    grok_brutal_honesty JSON,
                    grok_controversy_analysis JSON,
                    -- Ensure poster fields exist for saving extended Grok data
                    grok_movie_poster_url TEXT,
                    grok_poster_prompt TEXT,
                    grok_raw_response LONGTEXT,
                    
                    -- OpenAI Analysis Results
                    openai_score DECIMAL(3,1),
                    openai_recommendation VARCHAR(50),
                    openai_verdict TEXT,
                    openai_confidence DECIMAL(3,2),
                    openai_commercial_assessment JSON,
                    openai_technical_craft JSON,
                    openai_industry_comparison JSON,
                    openai_raw_response LONGTEXT,
                    openai_movie_poster_url TEXT,
                    openai_poster_prompt TEXT,
                    
                    -- PiAPI Poster Generation Results
                    piapi_poster_url TEXT,
                    piapi_poster_prompt TEXT,
                    piapi_poster_cost DECIMAL(6,4),
                    piapi_poster_success BOOLEAN,
                    piapi_poster_error TEXT,
                    
                    -- Processing Details
                    ai_model VARCHAR(100),
                    confidence_level DECIMAL(3,2),
                    processing_time DECIMAL(8,2),
                    cost DECIMAL(10,4),
                    
                    -- Status and Metadata
                    status ENUM('pending', 'processing', 'completed', 'error') DEFAULT 'pending',
                    error_message TEXT,
                    raw_api_request LONGTEXT,
                    raw_api_response LONGTEXT,
                    -- Budget fields
                    user_proposed_budget DECIMAL(12,2) NULL,
                    budget_currency VARCHAR(10) DEFAULT 'USD',
                    budget_category VARCHAR(20) NULL,
                    ai_budget_min DECIMAL(12,2) NULL,
                    ai_budget_optimal DECIMAL(12,2) NULL,
                    ai_budget_max DECIMAL(12,2) NULL,
                    budget_notes JSON,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    INDEX idx_user_id (user_id),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                )
            """)
            
            # Create api_usage_tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage_tracking (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    analysis_id VARCHAR(255),
                    api_provider VARCHAR(50) NOT NULL,
                    model_name VARCHAR(100) NOT NULL,
                    
                    -- Usage Metrics
                    input_tokens INT DEFAULT 0,
                    output_tokens INT DEFAULT 0,
                    total_tokens INT DEFAULT 0,
                    cost DECIMAL(10,6) NOT NULL,
                    
                    -- Request Details
                    request_type VARCHAR(50) NOT NULL,
                    processing_time DECIMAL(8,2),
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    INDEX idx_user_id (user_id),
                    INDEX idx_api_provider (api_provider),
                    INDEX idx_created_at (created_at)
                )
            """)
            
            # Create user_usage_summary table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_usage_summary (
                    user_id VARCHAR(255) PRIMARY KEY,
                    
                    -- Monthly Usage (current month)
                    monthly_analyses_count INT DEFAULT 0,
                    monthly_cost DECIMAL(10,4) DEFAULT 0,
                    monthly_tokens INT DEFAULT 0,
                    
                    -- All-time Usage
                    total_analyses_count INT DEFAULT 0,
                    total_cost DECIMAL(10,4) DEFAULT 0,
                    total_tokens INT DEFAULT 0,
                    
                    -- Last Activity
                    last_analysis_at TIMESTAMP NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            logger.info("✅ Database tables initialized successfully")
            
        except Error as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise
    
    def save_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Save analysis results to database"""
        try:
            cursor = self.connection.cursor()
            # Defensive: ensure JSON types are serialized
            try:
                if isinstance(analysis_data.get('budget_notes'), (dict, list)):
                    analysis_data['budget_notes'] = json.dumps(analysis_data['budget_notes'])
            except Exception:
                pass
            
            # Defensive: ensure timestamp format compatible with MySQL for perplexity_research_date
            try:
                research_date = analysis_data.get('perplexity_research_date')
                if research_date:
                    # Accept datetime, or ISO strings like 2025-08-23T08:15:30.123456
                    if isinstance(research_date, datetime):
                        analysis_data['perplexity_research_date'] = research_date.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(research_date, str):
                        # Convert ISO 8601 to MySQL DATETIME
                        iso_str = research_date.replace('Z', '+00:00')
                        try:
                            dt = datetime.fromisoformat(iso_str)
                            analysis_data['perplexity_research_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except Exception:
                            # Fallback: try trimming at 'T'
                            if 'T' in research_date:
                                analysis_data['perplexity_research_date'] = research_date.split('T')[0] + ' ' + research_date.split('T')[1].split('.')[0]
                            else:
                                # As a last resort, drop the value to avoid insert failure
                                analysis_data['perplexity_research_date'] = None
            except Exception:
                # Do not block save on formatting issues
                pass
            
            query = """
                INSERT INTO screenplay_analyses (
                    id, user_id, title, original_filename, file_path, file_size,
                    genre, detected_genre, subgenre, overall_score, recommendation,
                    one_line_verdict, logline, executive_summary, top_strengths, key_weaknesses,
                    suggestions, commercial_viability, target_audience, comparable_films,
                    casting_suggestions, structural_analysis, character_analysis, thematic_depth,
                    craft_evaluation, genre_mastery, improvement_strategies, casting_vision,
                    director_recommendation, grok_score, grok_recommendation, grok_verdict, grok_confidence,
                    grok_cultural_analysis, grok_brutal_honesty, grok_controversy_analysis,
                    grok_movie_poster_url, grok_poster_prompt,
                    openai_score, openai_recommendation, openai_verdict, openai_confidence,
                    openai_commercial_assessment, openai_technical_craft, openai_industry_comparison, openai_raw_response,
                    openai_movie_poster_url, openai_poster_prompt,
                    gpt5_score, gpt5_recommendation, gpt5_executive_assessment, gpt5_reasoning_depth,
                    gpt5_reasoning_tokens, gpt5_confidence, gpt5_processing_time, gpt5_cost,
                    gpt5_character_voice_analysis, gpt5_dialogue_authenticity, gpt5_prose_quality,
                    gpt5_emotional_beat_mapping, gpt5_professional_markers, gpt5_amateur_indicators,
                    gpt5_industry_comparison, gpt5_raw_response,
                    deepseek_budget_optimization, deepseek_confidence, deepseek_cost, deepseek_error_message,
                    deepseek_financial_score, deepseek_processing_time, deepseek_production_optimization,
                    deepseek_raw_response, deepseek_recommendation, deepseek_risk_assessment,
                    deepseek_roi_analysis, deepseek_success, deepseek_platform_analysis,
                    perplexity_competitive_advantage, perplexity_competitive_analysis, perplexity_cost,
                    perplexity_data_freshness, perplexity_distribution_strategy, perplexity_error_message,
                    perplexity_financial_intelligence, perplexity_industry_reports, perplexity_market_score,
                    perplexity_processing_time, perplexity_recommendation, perplexity_research_date,
                    perplexity_sources_cited, perplexity_success, perplexity_talent_intelligence,
                    source_adaptation_notes, source_author, source_commercial_implications,
                    source_confidence_score, source_cost, source_description, source_error_message,
                    source_has_material, source_legal_considerations, source_market_advantages,
                    source_potential_challenges, source_processing_time, source_raw_detection_text,
                    source_success, source_title, source_type,
                    poster_collection_title, poster_collection_genre, poster_total_cost,
                    poster_total_time, poster_success_count, poster_best_url,
                    poster_best_source, poster_variations_json,
                    ai_model, confidence_level, processing_time, cost, status, 
                    raw_api_request, raw_api_response, grok_raw_response,
                    user_proposed_budget, budget_currency, budget_category,
                    ai_budget_min, ai_budget_optimal, ai_budget_max, budget_notes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    user_id = VALUES(user_id),
                    title = VALUES(title),
                    original_filename = VALUES(original_filename),
                    file_path = VALUES(file_path),
                    file_size = VALUES(file_size),
                    genre = VALUES(genre),
                    detected_genre = VALUES(detected_genre),
                    subgenre = VALUES(subgenre),
                    overall_score = VALUES(overall_score),
                    recommendation = VALUES(recommendation),
                    one_line_verdict = VALUES(one_line_verdict),
                    logline = VALUES(logline),
                    executive_summary = VALUES(executive_summary),
                    top_strengths = VALUES(top_strengths),
                    key_weaknesses = VALUES(key_weaknesses),
                    suggestions = VALUES(suggestions),
                    commercial_viability = VALUES(commercial_viability),
                    target_audience = VALUES(target_audience),
                    comparable_films = VALUES(comparable_films),
                    casting_suggestions = VALUES(casting_suggestions),
                    structural_analysis = VALUES(structural_analysis),
                    character_analysis = VALUES(character_analysis),
                    thematic_depth = VALUES(thematic_depth),
                    craft_evaluation = VALUES(craft_evaluation),
                    genre_mastery = VALUES(genre_mastery),
                    improvement_strategies = VALUES(improvement_strategies),
                    casting_vision = VALUES(casting_vision),
                    director_recommendation = VALUES(director_recommendation),
                    grok_score = VALUES(grok_score),
                    grok_recommendation = VALUES(grok_recommendation),
                    grok_verdict = VALUES(grok_verdict),
                    grok_confidence = VALUES(grok_confidence),
                    grok_cultural_analysis = VALUES(grok_cultural_analysis),
                    grok_brutal_honesty = VALUES(grok_brutal_honesty),
                    grok_controversy_analysis = VALUES(grok_controversy_analysis),
                    grok_movie_poster_url = VALUES(grok_movie_poster_url),
                    grok_poster_prompt = VALUES(grok_poster_prompt),
                    openai_score = VALUES(openai_score),
                    openai_recommendation = VALUES(openai_recommendation),
                    openai_verdict = VALUES(openai_verdict),
                    openai_confidence = VALUES(openai_confidence),
                    openai_commercial_assessment = VALUES(openai_commercial_assessment),
                    openai_technical_craft = VALUES(openai_technical_craft),
                    openai_industry_comparison = VALUES(openai_industry_comparison),
                    openai_raw_response = VALUES(openai_raw_response),
                    openai_movie_poster_url = VALUES(openai_movie_poster_url),
                    openai_poster_prompt = VALUES(openai_poster_prompt),
                    gpt5_score = VALUES(gpt5_score),
                    gpt5_recommendation = VALUES(gpt5_recommendation),
                    gpt5_executive_assessment = VALUES(gpt5_executive_assessment),
                    gpt5_reasoning_depth = VALUES(gpt5_reasoning_depth),
                    gpt5_reasoning_tokens = VALUES(gpt5_reasoning_tokens),
                    gpt5_confidence = VALUES(gpt5_confidence),
                    gpt5_processing_time = VALUES(gpt5_processing_time),
                    gpt5_cost = VALUES(gpt5_cost),
                    gpt5_character_voice_analysis = VALUES(gpt5_character_voice_analysis),
                    gpt5_dialogue_authenticity = VALUES(gpt5_dialogue_authenticity),
                    gpt5_prose_quality = VALUES(gpt5_prose_quality),
                    gpt5_emotional_beat_mapping = VALUES(gpt5_emotional_beat_mapping),
                    gpt5_professional_markers = VALUES(gpt5_professional_markers),
                    gpt5_amateur_indicators = VALUES(gpt5_amateur_indicators),
                    gpt5_industry_comparison = VALUES(gpt5_industry_comparison),
                    gpt5_raw_response = VALUES(gpt5_raw_response),
                    deepseek_budget_optimization = VALUES(deepseek_budget_optimization),
                    deepseek_confidence = VALUES(deepseek_confidence),
                    deepseek_cost = VALUES(deepseek_cost),
                    deepseek_error_message = VALUES(deepseek_error_message),
                    deepseek_financial_score = VALUES(deepseek_financial_score),
                    deepseek_processing_time = VALUES(deepseek_processing_time),
                    deepseek_production_optimization = VALUES(deepseek_production_optimization),
                    deepseek_raw_response = VALUES(deepseek_raw_response),
                    deepseek_recommendation = VALUES(deepseek_recommendation),
                    deepseek_risk_assessment = VALUES(deepseek_risk_assessment),
                    deepseek_roi_analysis = VALUES(deepseek_roi_analysis),
                    deepseek_success = VALUES(deepseek_success),
                    deepseek_platform_analysis = VALUES(deepseek_platform_analysis),
                    perplexity_competitive_advantage = VALUES(perplexity_competitive_advantage),
                    perplexity_competitive_analysis = VALUES(perplexity_competitive_analysis),
                    perplexity_cost = VALUES(perplexity_cost),
                    perplexity_data_freshness = VALUES(perplexity_data_freshness),
                    perplexity_distribution_strategy = VALUES(perplexity_distribution_strategy),
                    perplexity_error_message = VALUES(perplexity_error_message),
                    perplexity_financial_intelligence = VALUES(perplexity_financial_intelligence),
                    perplexity_industry_reports = VALUES(perplexity_industry_reports),
                    perplexity_market_score = VALUES(perplexity_market_score),
                    perplexity_processing_time = VALUES(perplexity_processing_time),
                    perplexity_recommendation = VALUES(perplexity_recommendation),
                    perplexity_research_date = VALUES(perplexity_research_date),
                    perplexity_sources_cited = VALUES(perplexity_sources_cited),
                    perplexity_success = VALUES(perplexity_success),
                    perplexity_talent_intelligence = VALUES(perplexity_talent_intelligence),
                    source_adaptation_notes = VALUES(source_adaptation_notes),
                    source_author = VALUES(source_author),
                    source_commercial_implications = VALUES(source_commercial_implications),
                    source_confidence_score = VALUES(source_confidence_score),
                    source_cost = VALUES(source_cost),
                    source_description = VALUES(source_description),
                    source_error_message = VALUES(source_error_message),
                    source_has_material = VALUES(source_has_material),
                    source_legal_considerations = VALUES(source_legal_considerations),
                    source_market_advantages = VALUES(source_market_advantages),
                    source_potential_challenges = VALUES(source_potential_challenges),
                    source_processing_time = VALUES(source_processing_time),
                    source_raw_detection_text = VALUES(source_raw_detection_text),
                    source_success = VALUES(source_success),
                    source_title = VALUES(source_title),
                    source_type = VALUES(source_type),
                    poster_collection_title = VALUES(poster_collection_title),
                    poster_collection_genre = VALUES(poster_collection_genre),
                    poster_total_cost = VALUES(poster_total_cost),
                    poster_total_time = VALUES(poster_total_time),
                    poster_success_count = VALUES(poster_success_count),
                    poster_best_url = VALUES(poster_best_url),
                    poster_best_source = VALUES(poster_best_source),
                    poster_variations_json = VALUES(poster_variations_json),
                    ai_model = VALUES(ai_model),
                    confidence_level = VALUES(confidence_level),
                    processing_time = VALUES(processing_time),
                    cost = VALUES(cost),
                    status = VALUES(status),
                    raw_api_request = VALUES(raw_api_request),
                    raw_api_response = VALUES(raw_api_response),
                    grok_raw_response = VALUES(grok_raw_response),
                    user_proposed_budget = VALUES(user_proposed_budget),
                    budget_currency = VALUES(budget_currency),
                    budget_category = VALUES(budget_category),
                    ai_budget_min = VALUES(ai_budget_min),
                    ai_budget_optimal = VALUES(ai_budget_optimal),
                    ai_budget_max = VALUES(ai_budget_max),
                    budget_notes = VALUES(budget_notes),
                    updated_at = CURRENT_TIMESTAMP
            """
            
            # Convert dictionary to tuple in the correct order, with safe access
            values = (
                analysis_data.get('id'), analysis_data.get('user_id'), analysis_data.get('title'), 
                analysis_data.get('original_filename'), analysis_data.get('file_path'), analysis_data.get('file_size'),
                analysis_data.get('genre'), analysis_data.get('detected_genre'), analysis_data.get('subgenre'), 
                analysis_data.get('overall_score'), analysis_data.get('recommendation'),
                analysis_data.get('one_line_verdict'), analysis_data.get('logline'), analysis_data.get('executive_summary'), 
                analysis_data.get('top_strengths'), analysis_data.get('key_weaknesses'),
                analysis_data.get('suggestions'), analysis_data.get('commercial_viability'), analysis_data.get('target_audience'), 
                analysis_data.get('comparable_films'),
                analysis_data.get('casting_suggestions'), analysis_data.get('structural_analysis'), analysis_data.get('character_analysis'), 
                analysis_data.get('thematic_depth'),
                analysis_data.get('craft_evaluation'), analysis_data.get('genre_mastery'), analysis_data.get('improvement_strategies'), 
                analysis_data.get('casting_vision'),
                analysis_data.get('director_recommendation'), analysis_data.get('grok_score'), analysis_data.get('grok_recommendation'), 
                analysis_data.get('grok_verdict'), analysis_data.get('grok_confidence'),
                analysis_data.get('grok_cultural_analysis'), analysis_data.get('grok_brutal_honesty'), analysis_data.get('grok_controversy_analysis'),
                analysis_data.get('grok_movie_poster_url'), analysis_data.get('grok_poster_prompt'),
                analysis_data.get('openai_score'), analysis_data.get('openai_recommendation'), analysis_data.get('openai_verdict'), 
                analysis_data.get('openai_confidence'),
                analysis_data.get('openai_commercial_assessment'), analysis_data.get('openai_technical_craft'), 
                analysis_data.get('openai_industry_comparison'), analysis_data.get('openai_raw_response'),
                analysis_data.get('openai_movie_poster_url'), analysis_data.get('openai_poster_prompt'),
                analysis_data.get('gpt5_score'), analysis_data.get('gpt5_recommendation'), analysis_data.get('gpt5_executive_assessment'),
                analysis_data.get('gpt5_reasoning_depth'), analysis_data.get('gpt5_reasoning_tokens'), analysis_data.get('gpt5_confidence'),
                analysis_data.get('gpt5_processing_time'), analysis_data.get('gpt5_cost'),
                analysis_data.get('gpt5_character_voice_analysis'), analysis_data.get('gpt5_dialogue_authenticity'),
                analysis_data.get('gpt5_prose_quality'), analysis_data.get('gpt5_emotional_beat_mapping'),
                analysis_data.get('gpt5_professional_markers'), analysis_data.get('gpt5_amateur_indicators'),
                analysis_data.get('gpt5_industry_comparison'), analysis_data.get('gpt5_raw_response'),
                # DeepSeek fields
                analysis_data.get('deepseek_budget_optimization'), analysis_data.get('deepseek_confidence'), 
                analysis_data.get('deepseek_cost'), analysis_data.get('deepseek_error_message'),
                analysis_data.get('deepseek_financial_score'), analysis_data.get('deepseek_processing_time'), 
                analysis_data.get('deepseek_production_optimization'),
                analysis_data.get('deepseek_raw_response'), analysis_data.get('deepseek_recommendation'), 
                analysis_data.get('deepseek_risk_assessment'),
                analysis_data.get('deepseek_roi_analysis'), analysis_data.get('deepseek_success'), analysis_data.get('deepseek_platform_analysis'),
                # Perplexity fields
                analysis_data.get('perplexity_competitive_advantage'), analysis_data.get('perplexity_competitive_analysis'), 
                analysis_data.get('perplexity_cost'),
                analysis_data.get('perplexity_data_freshness'), analysis_data.get('perplexity_distribution_strategy'), 
                analysis_data.get('perplexity_error_message'),
                analysis_data.get('perplexity_financial_intelligence'), analysis_data.get('perplexity_industry_reports'), 
                analysis_data.get('perplexity_market_score'),
                analysis_data.get('perplexity_processing_time'), analysis_data.get('perplexity_recommendation'), 
                analysis_data.get('perplexity_research_date'),
                analysis_data.get('perplexity_sources_cited'), analysis_data.get('perplexity_success'), 
                analysis_data.get('perplexity_talent_intelligence'),
                # Source material fields
                analysis_data.get('source_adaptation_notes'), analysis_data.get('source_author'), 
                analysis_data.get('source_commercial_implications'),
                analysis_data.get('source_confidence_score'), analysis_data.get('source_cost'), 
                analysis_data.get('source_description'), analysis_data.get('source_error_message'),
                analysis_data.get('source_has_material'), analysis_data.get('source_legal_considerations'), 
                analysis_data.get('source_market_advantages'),
                analysis_data.get('source_potential_challenges'), analysis_data.get('source_processing_time'), 
                analysis_data.get('source_raw_detection_text'),
                analysis_data.get('source_success'), analysis_data.get('source_title'), analysis_data.get('source_type'),
                # Poster collection fields
                analysis_data.get('poster_collection_title'), analysis_data.get('poster_collection_genre'),
                analysis_data.get('poster_total_cost'), analysis_data.get('poster_total_time'),
                analysis_data.get('poster_success_count'), analysis_data.get('poster_best_url'),
                analysis_data.get('poster_best_source'), analysis_data.get('poster_variations_json'),
                # Standard fields
                analysis_data.get('ai_model'), analysis_data.get('confidence_level'), analysis_data.get('processing_time'), 
                analysis_data.get('cost'), analysis_data.get('status'),
                analysis_data.get('raw_api_request'), analysis_data.get('raw_api_response'), analysis_data.get('grok_raw_response'),
                # Budget fields
                analysis_data.get('user_proposed_budget'), analysis_data.get('budget_currency') or 'USD', analysis_data.get('budget_category'),
                analysis_data.get('ai_budget_min'), analysis_data.get('ai_budget_optimal'), analysis_data.get('ai_budget_max'), analysis_data.get('budget_notes')
            )
            cursor.execute(query, values)
            self.connection.commit()
            return True
            
        except Error as e:
            logger.error(f"❌ Error saving analysis: {e}")
            return False

    def insert_initial_analysis(self, initial_data: Dict[str, Any]) -> bool:
        """Insert an initial minimal analysis row to avoid placeholder mismatches"""
        try:
            cursor = self.connection.cursor()

            query = (
                "INSERT INTO screenplay_analyses ("
                "id, user_id, title, original_filename, file_path, file_size, "
                "genre, ai_model, status, user_proposed_budget"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "title = VALUES(title), original_filename = VALUES(original_filename), "
                "file_path = VALUES(file_path), file_size = VALUES(file_size), "
                "genre = VALUES(genre), ai_model = VALUES(ai_model), status = VALUES(status), "
                "user_proposed_budget = VALUES(user_proposed_budget), updated_at = CURRENT_TIMESTAMP"
            )

            values = (
                initial_data.get('id'), initial_data.get('user_id'), initial_data.get('title'),
                initial_data.get('original_filename'), initial_data.get('file_path'), initial_data.get('file_size'),
                initial_data.get('genre'), initial_data.get('ai_model'), initial_data.get('status'),
                initial_data.get('user_proposed_budget')
            )

            cursor.execute(query, values)
            self.connection.commit()
            return True
        
        except Error as e:
            logger.error(f"❌ Error inserting initial analysis: {e}")
            return False
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM screenplay_analyses WHERE id = %s", (analysis_id,))
            result = cursor.fetchone()
            
            if result:
                # Parse JSON fields
                json_fields = [
                    'top_strengths', 'key_weaknesses', 'suggestions', 'comparable_films', 
                    'casting_suggestions', 'improvement_strategies', 'casting_vision',
                    'grok_cultural_analysis', 'grok_brutal_honesty', 'grok_controversy_analysis',
                    'openai_commercial_assessment', 'openai_technical_craft', 'openai_industry_comparison',
                    'gpt5_executive_assessment', 'gpt5_character_voice_analysis', 'gpt5_dialogue_authenticity', 'gpt5_prose_quality',
                    'gpt5_emotional_beat_mapping', 'gpt5_professional_markers', 'gpt5_amateur_indicators',
                    'gpt5_industry_comparison',
                    # Source material fields that need JSON parsing
                    'source_market_advantages', 'source_market_challenges'
                ]
                for field in json_fields:
                    if result.get(field):
                        try:
                            result[field] = json.loads(result[field])
                        except (json.JSONDecodeError, TypeError):
                            # If JSON parsing fails, keep as string
                            pass
            
            return result
            
        except Error as e:
            logger.error(f"❌ Error getting analysis: {e}")
            return None
    
    def get_user_analyses(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all analyses for a user"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM screenplay_analyses 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (user_id, limit, offset))
            results = cursor.fetchall()
            
            # Parse JSON fields for each result
            json_fields = ['top_strengths', 'key_weaknesses', 'suggestions', 'comparable_films', 'casting_suggestions']
            for result in results:
                for field in json_fields:
                    if result[field]:
                        result[field] = json.loads(result[field])
            
            return results
            
        except Error as e:
            logger.error(f"❌ Error getting user analyses: {e}")
            return []
    
    def update_analysis_status(self, analysis_id: str, status: str, error_message: str = None) -> bool:
        """Update analysis status"""
        try:
            cursor = self.connection.cursor()
            if error_message:
                cursor.execute(
                    "UPDATE screenplay_analyses SET status = %s, error_message = %s WHERE id = %s",
                    (status, error_message, analysis_id)
                )
            else:
                cursor.execute(
                    "UPDATE screenplay_analyses SET status = %s WHERE id = %s",
                    (status, analysis_id)
                )
            self.connection.commit()
            return True
            
        except Error as e:
            logger.error(f"❌ Error updating analysis status: {e}")
            return False
    
    def track_api_usage(self, usage_data: Dict[str, Any]) -> bool:
        """Track API usage for cost monitoring"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO api_usage_tracking (
                    user_id, analysis_id, api_provider, model_name,
                    input_tokens, output_tokens, total_tokens, cost,
                    request_type, processing_time, success, error_message
                ) VALUES (
                    %(user_id)s, %(analysis_id)s, %(api_provider)s, %(model_name)s,
                    %(input_tokens)s, %(output_tokens)s, %(total_tokens)s, %(cost)s,
                    %(request_type)s, %(processing_time)s, %(success)s, %(error_message)s
                )
            """
            
            cursor.execute(query, usage_data)
            self.connection.commit()
            
            # Update user usage summary
            self.update_user_usage_summary(usage_data['user_id'], usage_data['cost'], usage_data['total_tokens'])
            
            return True
            
        except Error as e:
            logger.error(f"❌ Error tracking API usage: {e}")
            return False
    
    def update_user_usage_summary(self, user_id: str, cost: float, tokens: int) -> bool:
        """Update user usage summary"""
        try:
            cursor = self.connection.cursor()
            
            # Insert or update user usage summary
            query = """
                INSERT INTO user_usage_summary (
                    user_id, monthly_analyses_count, monthly_cost, monthly_tokens,
                    total_analyses_count, total_cost, total_tokens, last_analysis_at
                ) VALUES (
                    %s, 1, %s, %s, 1, %s, %s, NOW()
                ) ON DUPLICATE KEY UPDATE
                    monthly_analyses_count = monthly_analyses_count + 1,
                    monthly_cost = monthly_cost + %s,
                    monthly_tokens = monthly_tokens + %s,
                    total_analyses_count = total_analyses_count + 1,
                    total_cost = total_cost + %s,
                    total_tokens = total_tokens + %s,
                    last_analysis_at = NOW()
            """
            
            cursor.execute(query, (user_id, cost, tokens, cost, tokens, cost, tokens, cost, tokens))
            self.connection.commit()
            return True
            
        except Error as e:
            logger.error(f"❌ Error updating user usage summary: {e}")
            return False
    
    def get_user_usage_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user usage statistics"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_usage_summary WHERE user_id = %s", (user_id,))
            return cursor.fetchone()
            
        except Error as e:
            logger.error(f"❌ Error getting user usage stats: {e}")
            return None
