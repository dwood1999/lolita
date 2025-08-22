"""
API Cost Tracking and Usage Monitoring
Tracks API usage, costs, and user limits
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from database import ScreenplayDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostTracker:
    """Track API costs and user usage"""
    
    def __init__(self):
        self.db = ScreenplayDatabase()
        
        # API pricing (per 1M tokens)
        self.pricing = {
            'anthropic': {
                'claude-3-5-sonnet': {
                    'input': 3.0 / 1_000_000,
                    'output': 15.0 / 1_000_000
                }
            },
            'openai': {
                'gpt-4o': {
                    'input': 5.0 / 1_000_000,
                    'output': 15.0 / 1_000_000
                },
                'gpt-5': {  # Future pricing estimate
                    'input': 10.0 / 1_000_000,
                    'output': 30.0 / 1_000_000
                }
            },
            'xai': {
                'grok-4-latest': {
                    'input': 10.0 / 1_000_000,
                    'output': 30.0 / 1_000_000
                }
            }
        }
        
        logger.info("💰 Cost Tracker initialized")
    
    def track_usage(
        self,
        user_id: str,
        analysis_id: str,
        api_provider: str,
        model_name: str,
        cost: float,
        processing_time: float,
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        error_message: Optional[str] = None
    ) -> bool:
        """Track API usage and update user statistics"""
        
        try:
            total_tokens = input_tokens + output_tokens
            
            usage_data = {
                'user_id': user_id,
                'analysis_id': analysis_id,
                'api_provider': api_provider,
                'model_name': model_name,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': total_tokens,
                'cost': cost,
                'request_type': 'screenplay_analysis',
                'processing_time': processing_time,
                'success': success,
                'error_message': error_message
            }
            
            # Save to database
            if self.db.track_api_usage(usage_data):
                logger.info(f"💰 Usage tracked: {user_id} - ${cost:.4f} ({total_tokens} tokens)")
                return True
            else:
                logger.error(f"❌ Failed to track usage for {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cost tracking error: {e}")
            return False
    
    def get_user_costs(self, user_id: str) -> Dict[str, Any]:
        """Get user cost summary"""
        
        try:
            usage_stats = self.db.get_user_usage_stats(user_id)
            
            if not usage_stats:
                return {
                    'user_id': user_id,
                    'monthly_cost': 0.0,
                    'total_cost': 0.0,
                    'monthly_analyses': 0,
                    'total_analyses': 0,
                    'monthly_tokens': 0,
                    'total_tokens': 0,
                    'last_analysis': None
                }
            
            return {
                'user_id': user_id,
                'monthly_cost': float(usage_stats['monthly_cost']),
                'total_cost': float(usage_stats['total_cost']),
                'monthly_analyses': usage_stats['monthly_analyses_count'],
                'total_analyses': usage_stats['total_analyses_count'],
                'monthly_tokens': usage_stats['monthly_tokens'],
                'total_tokens': usage_stats['total_tokens'],
                'last_analysis': usage_stats['last_analysis_at']
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user costs: {e}")
            return {}
    
    def estimate_cost(
        self,
        text_length: int,
        api_provider: str = 'anthropic',
        model_name: str = 'claude-3-5-sonnet'
    ) -> float:
        """Estimate cost for text analysis"""
        
        try:
            # Rough token estimation (4 chars per token)
            estimated_input_tokens = text_length // 4
            estimated_output_tokens = 2000  # Typical analysis response
            
            pricing = self.pricing.get(api_provider, {}).get(model_name, {})
            
            if not pricing:
                logger.warning(f"⚠️ No pricing data for {api_provider}/{model_name}")
                return 0.0
            
            input_cost = estimated_input_tokens * pricing['input']
            output_cost = estimated_output_tokens * pricing['output']
            
            total_cost = input_cost + output_cost
            
            logger.info(f"💰 Cost estimate: ${total_cost:.4f} ({estimated_input_tokens + estimated_output_tokens} tokens)")
            
            return total_cost
            
        except Exception as e:
            logger.error(f"❌ Cost estimation error: {e}")
            return 0.0
    
    def check_user_limits(self, user_id: str) -> Dict[str, Any]:
        """Check if user is within usage limits"""
        
        try:
            usage_stats = self.db.get_user_usage_stats(user_id)
            
            # Default limits (can be made configurable)
            monthly_cost_limit = 50.0  # $50 per month
            monthly_analysis_limit = 100  # 100 analyses per month
            
            if not usage_stats:
                return {
                    'within_limits': True,
                    'monthly_cost_used': 0.0,
                    'monthly_cost_limit': monthly_cost_limit,
                    'monthly_analyses_used': 0,
                    'monthly_analysis_limit': monthly_analysis_limit,
                    'warnings': []
                }
            
            monthly_cost = float(usage_stats['monthly_cost'])
            monthly_analyses = usage_stats['monthly_analyses_count']
            
            warnings = []
            within_limits = True
            
            # Check cost limit
            if monthly_cost >= monthly_cost_limit:
                warnings.append(f"Monthly cost limit exceeded: ${monthly_cost:.2f} / ${monthly_cost_limit:.2f}")
                within_limits = False
            elif monthly_cost >= monthly_cost_limit * 0.8:
                warnings.append(f"Approaching monthly cost limit: ${monthly_cost:.2f} / ${monthly_cost_limit:.2f}")
            
            # Check analysis limit
            if monthly_analyses >= monthly_analysis_limit:
                warnings.append(f"Monthly analysis limit exceeded: {monthly_analyses} / {monthly_analysis_limit}")
                within_limits = False
            elif monthly_analyses >= monthly_analysis_limit * 0.8:
                warnings.append(f"Approaching monthly analysis limit: {monthly_analyses} / {monthly_analysis_limit}")
            
            return {
                'within_limits': within_limits,
                'monthly_cost_used': monthly_cost,
                'monthly_cost_limit': monthly_cost_limit,
                'monthly_analyses_used': monthly_analyses,
                'monthly_analysis_limit': monthly_analysis_limit,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking user limits: {e}")
            return {
                'within_limits': True,
                'warnings': [f"Error checking limits: {e}"]
            }
