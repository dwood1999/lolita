#!/usr/bin/env python3
"""
Budget Utilities for Screenplay Analysis
Provides consistent budget categorization and estimation logic
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BudgetTier:
    """Budget tier information"""
    name: str
    min_budget: float
    max_budget: Optional[float]
    description: str
    casting_implications: str
    production_notes: str
    target_audience: str
    distribution_strategy: str

# Define budget tiers with industry standards
BUDGET_TIERS = {
    "micro": BudgetTier(
        name="Micro-budget",
        min_budget=0,
        max_budget=1_000_000,
        description="Ultra-low budget independent films",
        casting_implications="Unknown actors, emerging talent, local actors willing to work for scale",
        production_notes="Single/few locations, minimal crew, practical effects only, handheld/basic camera work",
        target_audience="Film festival circuit, art house audiences, streaming platforms",
        distribution_strategy="Festival circuit → streaming/VOD → limited theatrical"
    ),
    "low": BudgetTier(
        name="Low-budget",
        min_budget=1_000_000,
        max_budget=5_000_000,
        description="Independent films with modest production values",
        casting_implications="Character actors, TV actors, one recognizable name possible",
        production_notes="Multiple locations possible, small crew, limited effects, professional equipment",
        target_audience="Independent film audiences, genre fans, arthouse + mainstream crossover",
        distribution_strategy="Festival premiere → platform release → selective theatrical"
    ),
    "mid": BudgetTier(
        name="Mid-budget",
        min_budget=5_000_000,
        max_budget=20_000_000,
        description="Professional productions with established talent",
        casting_implications="Established character actors, TV stars, emerging film stars",
        production_notes="Multiple locations, full crew, moderate effects, professional production values",
        target_audience="Mainstream genre audiences, star-driven demographics",
        distribution_strategy="Wide theatrical release, streaming after window, international sales"
    ),
    "high": BudgetTier(
        name="High-budget",
        min_budget=20_000_000,
        max_budget=50_000_000,
        description="Studio films with significant production values",
        casting_implications="A-list stars, established directors, proven talent packages",
        production_notes="Extensive locations, full studio resources, significant effects budget",
        target_audience="Wide mainstream appeal, international markets, franchise potential",
        distribution_strategy="Wide theatrical release, major marketing campaign, global distribution"
    ),
    "tentpole": BudgetTier(
        name="Tentpole",
        min_budget=50_000_000,
        max_budget=None,
        description="Event films and franchise starters",
        casting_implications="Major stars, A-list directors, established franchises or IP",
        production_notes="Multiple units, extensive VFX, global locations, massive crew",
        target_audience="Global audiences, all demographics, franchise/sequel potential required",
        distribution_strategy="Event release, massive marketing, global day-and-date, merchandising"
    )
}

def categorize_budget(budget: float) -> str:
    """
    Categorize budget amount into tier
    
    Args:
        budget: Budget amount in USD
        
    Returns:
        Budget tier key (micro, low, mid, high, tentpole)
    """
    if budget < 1_000_000:
        return "micro"
    elif budget < 5_000_000:
        return "low"
    elif budget < 20_000_000:
        return "mid"
    elif budget < 50_000_000:
        return "high"
    else:
        return "tentpole"

def get_budget_tier(budget: float) -> BudgetTier:
    """
    Get budget tier information for a given budget
    
    Args:
        budget: Budget amount in USD
        
    Returns:
        BudgetTier object with detailed information
    """
    tier_key = categorize_budget(budget)
    return BUDGET_TIERS[tier_key]

def estimate_budget_from_screenplay(
    screenplay_text: str, 
    title: str, 
    genre: str
) -> Tuple[float, float, float, str]:
    """
    Estimate budget range based on screenplay analysis
    
    Args:
        screenplay_text: Full screenplay text
        title: Screenplay title
        genre: Genre classification
        
    Returns:
        Tuple of (min_budget, optimal_budget, max_budget, reasoning)
    """
    
    # Base budget by genre (industry averages)
    genre_base_budgets = {
        "horror": (500_000, 3_000_000, 15_000_000),
        "thriller": (2_000_000, 8_000_000, 25_000_000),
        "drama": (1_000_000, 5_000_000, 20_000_000),
        "comedy": (3_000_000, 12_000_000, 35_000_000),
        "action": (15_000_000, 40_000_000, 150_000_000),
        "sci-fi": (10_000_000, 35_000_000, 200_000_000),
        "fantasy": (20_000_000, 60_000_000, 300_000_000),
        "romance": (2_000_000, 8_000_000, 25_000_000),
        "mystery": (3_000_000, 10_000_000, 30_000_000),
        "crime": (5_000_000, 15_000_000, 50_000_000)
    }
    
    # Default if genre not found
    base_min, base_optimal, base_max = genre_base_budgets.get(
        genre.lower(), (2_000_000, 10_000_000, 40_000_000)
    )
    
    # Analyze screenplay for budget-affecting elements
    text_lower = screenplay_text.lower()
    multiplier = 1.0
    reasoning_factors = []
    
    # Location complexity
    location_indicators = [
        ("multiple countries", 1.5, "international locations"),
        ("exotic location", 1.3, "exotic locations"),
        ("period setting", 1.4, "period setting requirements"),
        ("historical", 1.3, "historical setting"),
        ("space", 2.0, "space/futuristic setting"),
        ("underwater", 1.8, "underwater sequences"),
        ("desert", 1.2, "remote location filming")
    ]
    
    for indicator, mult, reason in location_indicators:
        if indicator in text_lower:
            multiplier *= mult
            reasoning_factors.append(reason)
    
    # Visual effects complexity
    vfx_indicators = [
        ("explosion", 1.3, "explosion sequences"),
        ("cgi", 1.4, "CGI requirements"),
        ("creature", 1.5, "creature/monster effects"),
        ("supernatural", 1.4, "supernatural effects"),
        ("flying", 1.3, "flying/aerial sequences"),
        ("car chase", 1.2, "vehicle action sequences"),
        ("gun fight", 1.1, "action sequences"),
        ("magic", 1.6, "magical effects")
    ]
    
    for indicator, mult, reason in vfx_indicators:
        if indicator in text_lower:
            multiplier *= mult
            reasoning_factors.append(reason)
    
    # Cast size indicators
    if text_lower.count("character") > 20:
        multiplier *= 1.2
        reasoning_factors.append("large ensemble cast")
    elif text_lower.count("character") < 5:
        multiplier *= 0.8
        reasoning_factors.append("minimal cast requirements")
    
    # Scale indicators
    scale_indicators = [
        ("army", 1.4, "military/army sequences"),
        ("crowd", 1.2, "crowd scenes"),
        ("stadium", 1.3, "large venue sequences"),
        ("city", 1.1, "urban filming complexity")
    ]
    
    for indicator, mult, reason in scale_indicators:
        if indicator in text_lower:
            multiplier *= mult
            reasoning_factors.append(reason)
    
    # Apply multiplier
    estimated_min = base_min * multiplier
    estimated_optimal = base_optimal * multiplier
    estimated_max = base_max * multiplier
    
    # Cap at reasonable limits
    estimated_min = min(estimated_min, 500_000_000)
    estimated_optimal = min(estimated_optimal, 500_000_000)
    estimated_max = min(estimated_max, 500_000_000)
    
    # Generate reasoning
    reasoning = f"Based on {genre} genre baseline"
    if reasoning_factors:
        reasoning += f" with adjustments for: {', '.join(reasoning_factors)}"
    reasoning += f". Genre base range: ${base_min:,.0f}-${base_max:,.0f}, adjusted by {multiplier:.1f}x multiplier."
    
    return estimated_min, estimated_optimal, estimated_max, reasoning

def get_casting_suggestions_by_budget(budget: float, genre: str) -> Dict[str, Any]:
    """
    Generate budget-appropriate casting suggestions
    
    Args:
        budget: Budget amount in USD
        genre: Genre classification
        
    Returns:
        Dictionary with casting strategy and suggestions
    """
    tier = get_budget_tier(budget)
    tier_key = categorize_budget(budget)
    
    casting_strategies = {
        "micro": {
            "lead_strategy": "Emerging talent, theater actors, local talent willing to work for scale",
            "supporting_strategy": "Non-professional actors, real people, documentary-style casting",
            "star_power": "Focus on raw talent over recognition",
            "agent_level": "Smaller agencies, self-represented actors, casting workshops",
            "typical_leads": ["Unknown theater actors", "Film school graduates", "Local talent"],
            "budget_allocation": "80% to lead roles, minimal supporting cast payments"
        },
        "low": {
            "lead_strategy": "Character actors with TV/indie credits, emerging stars from streaming",
            "supporting_strategy": "Mix of professionals and newcomers, local SAG actors",
            "star_power": "One recognizable face maximum, focus on ensemble strength",
            "agent_level": "Mid-tier agencies, boutique representation",
            "typical_leads": ["TV guest stars", "Indie film veterans", "Character actors"],
            "budget_allocation": "60% to leads, 40% distributed among supporting cast"
        },
        "mid": {
            "lead_strategy": "Established character actors, TV series regulars, emerging film stars",
            "supporting_strategy": "Professional character actors, recognizable TV faces",
            "star_power": "B-list lead or A-list supporting role possible",
            "agent_level": "Major agencies, established representation",
            "typical_leads": ["TV stars", "Character actors", "Indie darlings"],
            "budget_allocation": "50% to lead roles, balanced supporting cast investment"
        },
        "high": {
            "lead_strategy": "A-list stars, established leading actors, proven box office draws",
            "supporting_strategy": "Notable character actors, former leads in supporting roles",
            "star_power": "Major star power essential for this budget level",
            "agent_level": "Top-tier agencies (CAA, WME, UTA), A-list representation",
            "typical_leads": ["Movie stars", "Award winners", "Box office draws"],
            "budget_allocation": "40% to star salaries, high-quality supporting ensemble"
        },
        "tentpole": {
            "lead_strategy": "Franchise stars, global A-listers, proven tentpole leads",
            "supporting_strategy": "Star-studded ensemble, international appeal casting",
            "star_power": "Global recognition essential, franchise/sequel potential",
            "agent_level": "Top agencies, major production company relationships",
            "typical_leads": ["Global superstars", "Franchise anchors", "Award-winning A-listers"],
            "budget_allocation": "35% to lead stars, significant supporting star investment"
        }
    }
    
    # Genre-specific casting notes
    genre_casting = {
        "horror": "Prioritize unknown faces for authenticity, one recognizable lead for marketing",
        "comedy": "Comedic timing over star power, ensemble chemistry crucial",
        "action": "Physical capability and stunt work experience important",
        "drama": "Acting talent and emotional range prioritized over star power",
        "thriller": "Psychological intensity and screen presence essential",
        "sci-fi": "Comfort with technical dialogue and green screen work",
        "fantasy": "Physical casting for costume/makeup considerations",
        "romance": "Chemistry between leads paramount, audience appeal important"
    }
    
    strategy = casting_strategies.get(tier_key, casting_strategies["mid"])
    strategy["genre_considerations"] = genre_casting.get(genre.lower(), "Standard casting approach")
    strategy["budget_tier"] = tier.name
    strategy["budget_range"] = f"${tier.min_budget:,.0f}" + (f"-${tier.max_budget:,.0f}" if tier.max_budget else "+")
    
    return strategy

def format_budget_context_for_ai(budget: Optional[float], estimated_budget: Optional[Tuple[float, float, float, str]] = None) -> str:
    """
    Format budget context for AI prompt inclusion
    
    Args:
        budget: User-provided budget (if any)
        estimated_budget: AI-estimated budget tuple (if any)
        
    Returns:
        Formatted budget context string for AI prompts
    """
    if budget:
        tier = get_budget_tier(budget)
        return f"""
**BUDGET ANALYSIS: {tier.name} (${budget:,.0f})**
Production Context: {tier.description}
Casting Strategy: {tier.casting_implications}
Production Notes: {tier.production_notes}
Target Audience: {tier.target_audience}
Distribution: {tier.distribution_strategy}

Consider how this budget level affects all recommendations, especially casting suggestions and production feasibility.
"""
    elif estimated_budget:
        min_b, opt_b, max_b, reasoning = estimated_budget
        opt_tier = get_budget_tier(opt_b)
        return f"""
**BUDGET ANALYSIS: AI Estimated**
Estimated Range: ${min_b:,.0f} - ${max_b:,.0f}
Optimal Budget: ${opt_b:,.0f} ({opt_tier.name})
Reasoning: {reasoning}

Casting Strategy: {opt_tier.casting_implications}
Production Notes: {opt_tier.production_notes}

Base recommendations on the optimal budget estimate unless story elements justify higher/lower range.
"""
    else:
        return """
**BUDGET ANALYSIS: To be determined**
No budget specified - provide realistic budget recommendation based on story scope, genre requirements, and production complexity.
Include both conservative and ambitious budget scenarios in your analysis.
"""
