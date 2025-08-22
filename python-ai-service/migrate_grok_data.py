#!/usr/bin/env python3
"""
Migration script to reprocess existing Grok analyses and extract enhanced data
from raw responses that were truncated due to token limits.
"""

import json
import logging
from database import ScreenplayDatabase
from grok_analyzer import GrokAnalyzer, GrokResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_grok_enhanced_data():
    """Migrate existing Grok analyses to extract enhanced data from raw responses"""
    
    try:
        db = ScreenplayDatabase()
        analyzer = GrokAnalyzer()
        
        # Get all analyses with Grok data but missing enhanced fields
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, grok_raw_response, grok_score, grok_recommendation, grok_verdict, grok_confidence
            FROM screenplay_analyses 
            WHERE grok_raw_response IS NOT NULL 
            AND (grok_cultural_analysis IS NULL OR grok_brutal_honesty IS NULL)
            ORDER BY created_at DESC
        """)
        
        analyses = cursor.fetchall()
        logger.info(f"Found {len(analyses)} analyses to migrate")
        
        migrated_count = 0
        
        for analysis in analyses:
            try:
                analysis_id = analysis['id']
                raw_response = analysis['grok_raw_response']
                
                if not raw_response:
                    continue
                
                logger.info(f"Processing analysis: {analysis_id}")
                
                # Parse the raw response with our improved parser
                parsed_data = analyzer._parse_response(raw_response)
                
                # Create a GrokResult object
                grok_result = GrokResult(
                    score=parsed_data.get('score', analysis['grok_score'] or 0),
                    recommendation=parsed_data.get('recommendation', analysis['grok_recommendation'] or ''),
                    verdict=parsed_data.get('verdict', analysis['grok_verdict'] or ''),
                    processing_time=0.0,  # Not available for existing analyses
                    cost=0.0,  # Not available for existing analyses
                    confidence=parsed_data.get('confidence', analysis['grok_confidence'] or 0.7),
                    raw_response=raw_response,
                    cultural_reality_check=parsed_data.get('cultural_reality_check'),
                    brutal_honesty_assessment=parsed_data.get('brutal_honesty_assessment'),
                    controversy_analysis=parsed_data.get('controversy_analysis')
                )
                
                # Convert to database format
                db_data = analyzer.to_database_format(grok_result)
                
                # Update only the enhanced fields
                update_query = """
                    UPDATE screenplay_analyses 
                    SET grok_cultural_analysis = %s,
                        grok_brutal_honesty = %s,
                        grok_controversy_analysis = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                
                cursor.execute(update_query, (
                    db_data.get('grok_cultural_analysis'),
                    db_data.get('grok_brutal_honesty'),
                    db_data.get('grok_controversy_analysis'),
                    analysis_id
                ))
                
                db.connection.commit()
                migrated_count += 1
                
                logger.info(f"✅ Migrated analysis {analysis_id}")
                
                # Log what was extracted
                if db_data.get('grok_cultural_analysis'):
                    logger.info(f"  - Extracted cultural analysis ({len(db_data['grok_cultural_analysis'])} chars)")
                if db_data.get('grok_brutal_honesty'):
                    logger.info(f"  - Extracted brutal honesty ({len(db_data['grok_brutal_honesty'])} chars)")
                if db_data.get('grok_controversy_analysis'):
                    logger.info(f"  - Extracted controversy analysis ({len(db_data['grok_controversy_analysis'])} chars)")
                
            except Exception as e:
                logger.error(f"❌ Failed to migrate analysis {analysis_id}: {e}")
                continue
        
        logger.info(f"🎉 Migration completed! Migrated {migrated_count} analyses")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_grok_enhanced_data()
