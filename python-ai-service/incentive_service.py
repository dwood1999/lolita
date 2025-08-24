#!/usr/bin/env python3
"""
Film Incentive Lookup Service
Business logic layer for film incentive analysis and matching
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
from datetime import datetime, date

from incentive_models import (
    IncentiveDatabase, 
    FilmIncentive, 
    LocationRequirement, 
    AnalysisLocationMatch,
    find_best_incentives_for_budget
)

logger = logging.getLogger(__name__)

class IncentiveLookupService:
    """Business logic service for film incentive analysis"""
    
    def __init__(self):
        """Initialize the incentive lookup service"""
        self.db = IncentiveDatabase()
        logger.info("🎯 Incentive Lookup Service initialized")
    
    def find_optimal_incentives_for_production(
        self, 
        budget: float, 
        genre: Optional[str] = None,
        shooting_locations: Optional[List[str]] = None,
        production_duration_weeks: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Find optimal incentives for a film production with enhanced business logic
        
        Args:
            budget: Total production budget
            genre: Film genre (affects incentive eligibility)
            shooting_locations: Preferred or required shooting locations
            production_duration_weeks: Estimated production duration
            
        Returns:
            Comprehensive incentive analysis with recommendations
        """
        try:
            logger.info(f"🔍 Finding optimal incentives for ${budget:,.0f} {genre or 'unknown genre'} production")
            
            # Get base incentive matches
            base_incentives = find_best_incentives_for_budget(budget, limit=15)
            
            # Apply business logic filters and scoring
            enhanced_incentives = self._enhance_incentive_analysis(
                base_incentives, 
                genre, 
                shooting_locations, 
                production_duration_weeks
            )
            
            # Generate recommendations
            recommendations = self._generate_incentive_recommendations(enhanced_incentives, budget)
            
            # Calculate summary metrics
            summary = self._calculate_incentive_summary(enhanced_incentives, budget)
            
            result = {
                'budget': budget,
                'genre': genre,
                'analysis_timestamp': datetime.now().isoformat(),
                'incentive_options': enhanced_incentives,
                'recommendations': recommendations,
                'summary': summary,
                'total_options_analyzed': len(base_incentives),
                'qualified_options': len(enhanced_incentives)
            }
            
            logger.info(f"✅ Found {len(enhanced_incentives)} qualified incentive options")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error finding optimal incentives: {e}")
            return {
                'error': str(e),
                'budget': budget,
                'incentive_options': [],
                'recommendations': {},
                'summary': {}
            }
    
    def _enhance_incentive_analysis(
        self, 
        base_incentives: List[Dict[str, Any]], 
        genre: Optional[str],
        shooting_locations: Optional[List[str]],
        production_duration_weeks: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Apply business logic to enhance incentive analysis"""
        
        enhanced = []
        
        for incentive in base_incentives:
            enhanced_incentive = incentive.copy()
            
            # Initialize enhancement scores
            location_match_score = 1.0
            genre_compatibility_score = 1.0
            timing_feasibility_score = 1.0
            ease_of_application_score = 1.0
            
            # Location matching logic
            if shooting_locations:
                country = incentive.get('country', '').lower()
                region = incentive.get('region', '').lower() if incentive.get('region') else ''
                
                location_matches = any(
                    country in loc.lower() or (region and region in loc.lower())
                    for loc in shooting_locations
                )
                location_match_score = 1.2 if location_matches else 0.8
            
            # Genre compatibility scoring
            if genre:
                genre_score = self._calculate_genre_compatibility(genre, incentive)
                genre_compatibility_score = genre_score
            
            # Production timing analysis
            if production_duration_weeks and incentive.get('processing_time_days'):
                timing_score = self._calculate_timing_feasibility(
                    production_duration_weeks, 
                    incentive.get('processing_time_days', 60)
                )
                timing_feasibility_score = timing_score
            
            # Application ease scoring
            ease_score = self._calculate_application_ease(incentive)
            ease_of_application_score = ease_score
            
            # Calculate overall enhanced score
            enhancement_multiplier = (
                location_match_score * 
                genre_compatibility_score * 
                timing_feasibility_score * 
                ease_of_application_score
            )
            
            # Apply enhancement
            enhanced_incentive['enhanced_score'] = enhancement_multiplier
            enhanced_incentive['enhanced_savings'] = float(incentive['final_savings']) * min(enhancement_multiplier, 1.2)
            enhanced_incentive['location_match_score'] = location_match_score
            enhanced_incentive['genre_compatibility_score'] = genre_compatibility_score
            enhanced_incentive['timing_feasibility_score'] = timing_feasibility_score
            enhanced_incentive['ease_of_application_score'] = ease_of_application_score
            
            # Add business insights
            enhanced_incentive['business_insights'] = self._generate_business_insights(
                incentive, enhancement_multiplier
            )
            
            enhanced.append(enhanced_incentive)
        
        # Sort by enhanced score
        enhanced.sort(key=lambda x: x['enhanced_score'], reverse=True)
        
        return enhanced[:10]  # Return top 10 enhanced options
    
    def _calculate_genre_compatibility(self, genre: str, incentive: Dict[str, Any]) -> float:
        """Calculate how well a genre matches an incentive program"""
        
        # Genre-specific incentive preferences
        genre_preferences = {
            'action': {'countries': ['united states', 'canada', 'united kingdom'], 'bonus': 1.1},
            'drama': {'countries': ['canada', 'ireland', 'united kingdom'], 'bonus': 1.15},
            'comedy': {'countries': ['united states', 'canada', 'australia'], 'bonus': 1.05},
            'thriller': {'countries': ['united states', 'united kingdom', 'canada'], 'bonus': 1.1},
            'horror': {'countries': ['united states', 'canada', 'ireland'], 'bonus': 1.05},
            'romance': {'countries': ['ireland', 'united kingdom', 'australia'], 'bonus': 1.1},
            'sci-fi': {'countries': ['united states', 'united kingdom', 'canada'], 'bonus': 1.15},
            'fantasy': {'countries': ['united kingdom', 'ireland', 'united states'], 'bonus': 1.15},
            'documentary': {'countries': ['canada', 'ireland', 'united kingdom'], 'bonus': 1.2}
        }
        
        genre_lower = genre.lower()
        country_lower = incentive.get('country', '').lower()
        
        if genre_lower in genre_preferences:
            prefs = genre_preferences[genre_lower]
            if country_lower in prefs['countries']:
                return prefs['bonus']
        
        return 1.0  # Neutral score
    
    def _calculate_timing_feasibility(self, production_weeks: int, processing_days: int) -> float:
        """Calculate timing feasibility based on production schedule"""
        
        # Convert production weeks to total timeline including pre-production
        total_timeline_days = (production_weeks * 7) + 60  # Add 60 days for pre-production
        
        if processing_days <= 30:
            return 1.2  # Fast processing is excellent
        elif processing_days <= 60:
            return 1.1  # Reasonable processing time
        elif processing_days <= total_timeline_days * 0.5:
            return 1.0  # Acceptable timing
        elif processing_days <= total_timeline_days:
            return 0.9  # Tight but manageable
        else:
            return 0.7  # May cause delays
    
    def _calculate_application_ease(self, incentive: Dict[str, Any]) -> float:
        """Calculate how easy an incentive is to apply for and obtain"""
        
        base_score = 1.0
        requirements = incentive.get('requirements', {})
        
        if not requirements:
            return base_score
        
        # Penalize complex requirements
        complexity_factors = [
            'cultural_test', 'canadian_content', 'european_content',
            'local_crew_requirement', 'resident_workers', 'labour_requirement'
        ]
        
        complexity_count = sum(1 for factor in complexity_factors if factor in requirements)
        
        # Easier incentives get higher scores
        if complexity_count == 0:
            return 1.2  # Very straightforward
        elif complexity_count <= 2:
            return 1.1  # Reasonable requirements
        elif complexity_count <= 4:
            return 1.0  # Standard complexity
        else:
            return 0.9  # Complex requirements
    
    def _generate_business_insights(self, incentive: Dict[str, Any], enhancement_score: float) -> List[str]:
        """Generate business insights for an incentive"""
        
        insights = []
        
        # Performance insight
        if enhancement_score > 1.15:
            insights.append("⭐ Highly recommended - excellent match for your production")
        elif enhancement_score > 1.05:
            insights.append("✅ Good match - solid incentive option")
        elif enhancement_score < 0.9:
            insights.append("⚠️ Consider carefully - may have application challenges")
        
        # Financial insight
        savings_percentage = (float(incentive['final_savings']) / float(incentive['qualifying_spend'])) * 100
        if savings_percentage > 30:
            insights.append(f"💰 Exceptional savings: {savings_percentage:.1f}% of qualifying spend")
        elif savings_percentage > 20:
            insights.append(f"💵 Strong savings: {savings_percentage:.1f}% of qualifying spend")
        
        # Processing insight
        processing_days = incentive.get('processing_time_days')
        if processing_days and processing_days <= 30:
            insights.append(f"⚡ Fast approval: {processing_days} days typical processing")
        elif processing_days and processing_days > 90:
            insights.append(f"⏰ Plan ahead: {processing_days} days processing time")
        
        # Requirements insight
        requirements = incentive.get('requirements', {})
        if 'transferable' in requirements and requirements.get('transferable'):
            insights.append("🔄 Transferable credits - flexible for financing")
        
        return insights
    
    def _generate_incentive_recommendations(self, incentives: List[Dict[str, Any]], budget: float) -> Dict[str, Any]:
        """Generate strategic recommendations based on incentive analysis"""
        
        if not incentives:
            return {'strategy': 'No suitable incentives found for this budget range'}
        
        top_incentive = incentives[0]
        
        recommendations = {
            'primary_recommendation': {
                'location': f"{top_incentive['country']}, {top_incentive['region']}" if top_incentive.get('region') else top_incentive['country'],
                'savings': top_incentive['final_savings'],
                'percentage': top_incentive['percentage'],
                'reason': f"Best overall value with {top_incentive['enhanced_score']:.2f}x enhancement score"
            },
            'strategy_insights': [],
            'action_items': []
        }
        
        # Strategic insights
        total_savings = sum(float(inc['final_savings']) for inc in incentives[:3])
        if len(incentives) >= 3:
            recommendations['strategy_insights'].append(
                f"Multi-location strategy could yield ${total_savings:,.0f} in combined savings"
            )
        
        if top_incentive['enhanced_score'] > 1.1:
            recommendations['strategy_insights'].append(
                "Primary recommendation shows excellent compatibility with your production"
            )
        
        # Action items
        recommendations['action_items'] = [
            f"Research detailed requirements for {top_incentive['country']} incentive program", 
            f"Confirm budget allocation meets qualifying spend requirements",
            f"Plan application timeline and processing requirements"
        ]
        
        return recommendations
    
    def _calculate_incentive_summary(self, incentives: List[Dict[str, Any]], budget: float) -> Dict[str, Any]:
        """Calculate summary statistics for incentive analysis"""
        
        if not incentives:
            return {}
        
        total_potential_savings = sum(float(inc['final_savings']) for inc in incentives)
        average_percentage = sum(float(inc['percentage']) for inc in incentives) / len(incentives)
        best_savings = max(float(inc['final_savings']) for inc in incentives)
        
        # Find countries represented
        countries = list(set(inc['country'] for inc in incentives))
        
        return {
            'total_options': len(incentives),
            'total_potential_savings': total_potential_savings,
            'best_single_savings': best_savings,
            'average_incentive_percentage': round(average_percentage, 1),
            'countries_available': countries,
            'budget_optimization_potential': round((best_savings / budget) * 100, 1)
        }
    
    def analyze_location_requirements(self, screenplay_text: str, title: str) -> List[Dict[str, Any]]:
        """
        Extract and analyze location requirements from screenplay
        This would integrate with Claude for location analysis
        """
        # Placeholder for location analysis - would integrate with Claude
        # For now, return some basic location categories
        
        basic_locations = [
            {
                'location_type': 'primary',
                'description': 'Urban exteriors and interiors',
                'script_mentions': 10,
                'feasibility_score': 8.0,
                'estimated_days': 15,
                'special_requirements': {'permits_needed': True, 'period_setting': False}
            },
            {
                'location_type': 'secondary', 
                'description': 'Rural/countryside scenes',
                'script_mentions': 5,
                'feasibility_score': 6.0,
                'estimated_days': 8,
                'special_requirements': {'weather_dependent': True}
            }
        ]
        
        logger.info(f"📍 Analyzed {len(basic_locations)} location requirements for '{title}'")
        return basic_locations
    
    def create_comprehensive_incentive_report(
        self, 
        analysis_id: str, 
        budget: float, 
        genre: Optional[str] = None,
        screenplay_text: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive incentive analysis report for a screenplay
        """
        try:
            logger.info(f"📊 Creating comprehensive incentive report for analysis {analysis_id}")
            
            # Get optimal incentives
            incentive_analysis = self.find_optimal_incentives_for_production(
                budget=budget,
                genre=genre
            )
            
            # Analyze locations if screenplay provided
            location_analysis = []
            if screenplay_text and title:
                location_analysis = self.analyze_location_requirements(screenplay_text, title)
            
            # Create comprehensive report
            report = {
                'analysis_id': analysis_id,
                'report_timestamp': datetime.now().isoformat(),
                'production_details': {
                    'title': title,
                    'genre': genre,
                    'budget': budget
                },
                'incentive_analysis': incentive_analysis,
                'location_analysis': location_analysis,
                'executive_summary': self._create_executive_summary(incentive_analysis, budget),
                'next_steps': self._generate_next_steps(incentive_analysis)
            }
            
            logger.info(f"✅ Created comprehensive incentive report with {len(incentive_analysis.get('incentive_options', []))} options")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error creating incentive report: {e}")
            return {
                'analysis_id': analysis_id,
                'error': str(e),
                'report_timestamp': datetime.now().isoformat()
            }
    
    def _create_executive_summary(self, incentive_analysis: Dict[str, Any], budget: float) -> str:
        """Create executive summary of incentive analysis"""
        
        summary = incentive_analysis.get('summary', {})
        recommendations = incentive_analysis.get('recommendations', {})
        
        if not summary:
            return "Incentive analysis could not be completed."
        
        best_savings = summary.get('best_single_savings', 0)
        best_percentage = round((best_savings / budget) * 100, 1) if budget > 0 else 0
        total_options = summary.get('total_options', 0)
        
        primary_rec = recommendations.get('primary_recommendation', {})
        best_location = primary_rec.get('location', 'Unknown')
        
        summary_text = f"""
INCENTIVE ANALYSIS EXECUTIVE SUMMARY

Production Budget: ${budget:,.0f}
Best Incentive Option: {best_location}
Maximum Potential Savings: ${best_savings:,.0f} ({best_percentage}% of budget)
Total Qualified Options: {total_options}

RECOMMENDATION: {primary_rec.get('reason', 'Consider available incentive programs to optimize production costs.')}
        """.strip()
        
        return summary_text
    
    def _generate_next_steps(self, incentive_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps"""
        
        recommendations = incentive_analysis.get('recommendations', {})
        action_items = recommendations.get('action_items', [])
        
        if action_items:
            return action_items
        
        # Fallback next steps
        return [
            "Review available incentive programs",
            "Consult with local film commissions",
            "Prepare application documentation",
            "Plan production timeline around incentive requirements"
        ]

# ==================== SERVICE INSTANCE ====================

def get_incentive_service() -> IncentiveLookupService:
    """Get the incentive lookup service instance"""
    return IncentiveLookupService()
