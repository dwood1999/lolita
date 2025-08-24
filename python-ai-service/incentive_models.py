#!/usr/bin/env python3
"""
Film Incentive Models and CRUD Operations
Provides data access layer for film incentive tracking system
"""

import os
import json
import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

logger = logging.getLogger(__name__)

@dataclass
class FilmIncentive:
    """Film incentive data model"""
    id: Optional[int] = None
    country: str = ""
    region: Optional[str] = None
    incentive_type: str = ""  # tax_credit, rebate, grant, loan, infrastructure, service_credit
    percentage: Optional[float] = None
    max_credit: Optional[float] = None
    requirements: Optional[Dict[str, Any]] = None
    application_deadline: Optional[date] = None
    current_cap_remaining: Optional[float] = None
    is_active: bool = True
    minimum_spend: Optional[float] = None
    maximum_spend: Optional[float] = None
    processing_time_days: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

@dataclass
class LocationRequirement:
    """Location requirement data model"""
    id: Optional[int] = None
    analysis_id: str = ""
    location_type: str = ""  # primary, secondary, studio, exterior, interior, special
    description: str = ""
    script_mentions: int = 0
    feasibility_score: Optional[float] = None
    estimated_days: Optional[int] = None
    special_requirements: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

@dataclass
class AnalysisLocationMatch:
    """Analysis to incentive match data model"""
    id: Optional[int] = None
    analysis_id: str = ""
    incentive_id: int = 0
    location_requirement_id: int = 0
    match_score: Optional[float] = None
    estimated_savings: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class IncentiveDatabase:
    """Database operations for film incentive system"""
    
    def __init__(self):
        """Initialize database connection using same pattern as ScreenplayDatabase"""
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER") 
        self.password = os.getenv("DB_PASSWORD")
        
        # Fix password handling - match existing pattern
        if self.password:
            if self.password.startswith('"') and self.password.endswith('"'):
                self.password = self.password[1:-1]
            elif self.password.startswith("'") and self.password.endswith("'"):
                self.password = self.password[1:-1]
            if '\\$' in self.password:
                self.password = self.password.replace('\\$', '$')
        
        self.database = os.getenv("DB_NAME")
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
                charset='utf8mb4',
                use_unicode=True
            )
            logger.info("✅ Incentive database connected successfully")
        except Error as e:
            logger.error(f"❌ Incentive database connection error: {e}")
            raise

    def get_connection(self):
        """Get database connection, reconnect if needed"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    # ==================== FILM INCENTIVE CRUD ====================
    
    def get_all_incentives(self, active_only: bool = True) -> List[FilmIncentive]:
        """Get all film incentives"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            
            query = """
                SELECT id, country, region, incentive_type, percentage, max_credit,
                       requirements, application_deadline, current_cap_remaining,
                       is_active, minimum_spend, maximum_spend, processing_time_days,
                       created_at, updated_at, expires_at
                FROM film_incentives
            """
            
            if active_only:
                query += " WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW())"
            
            query += " ORDER BY percentage DESC"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            incentives = []
            for row in results:
                # Parse JSON requirements if present
                if row['requirements']:
                    try:
                        row['requirements'] = json.loads(row['requirements']) if isinstance(row['requirements'], str) else row['requirements']
                    except (json.JSONDecodeError, TypeError):
                        row['requirements'] = {}
                
                incentives.append(FilmIncentive(**row))
            
            logger.info(f"📋 Retrieved {len(incentives)} incentives")
            return incentives
            
        except Error as e:
            logger.error(f"❌ Error retrieving incentives: {e}")
            return []

    def get_incentives_by_country(self, country: str) -> List[FilmIncentive]:
        """Get incentives for a specific country"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            
            query = """
                SELECT id, country, region, incentive_type, percentage, max_credit,
                       requirements, application_deadline, current_cap_remaining,
                       is_active, minimum_spend, maximum_spend, processing_time_days,
                       created_at, updated_at, expires_at
                FROM film_incentives
                WHERE country = %s AND is_active = TRUE 
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY percentage DESC
            """
            
            cursor.execute(query, (country,))
            results = cursor.fetchall()
            
            incentives = []
            for row in results:
                if row['requirements']:
                    try:
                        row['requirements'] = json.loads(row['requirements']) if isinstance(row['requirements'], str) else row['requirements']
                    except (json.JSONDecodeError, TypeError):
                        row['requirements'] = {}
                
                incentives.append(FilmIncentive(**row))
            
            return incentives
            
        except Error as e:
            logger.error(f"❌ Error retrieving incentives for {country}: {e}")
            return []

    def find_matching_incentives(self, budget: float, min_percentage: float = 0.0) -> List[FilmIncentive]:
        """Find incentives matching budget and minimum percentage criteria"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            
            query = """
                SELECT id, country, region, incentive_type, percentage, max_credit,
                       requirements, application_deadline, current_cap_remaining,
                       is_active, minimum_spend, maximum_spend, processing_time_days,
                       created_at, updated_at, expires_at
                FROM film_incentives
                WHERE is_active = TRUE 
                AND (expires_at IS NULL OR expires_at > NOW())
                AND (minimum_spend IS NULL OR minimum_spend <= %s)
                AND (maximum_spend IS NULL OR maximum_spend >= %s)
                AND percentage >= %s
                AND (current_cap_remaining IS NULL OR current_cap_remaining > minimum_spend)
                ORDER BY percentage DESC
                LIMIT 10
            """
            
            cursor.execute(query, (budget, budget, min_percentage))
            results = cursor.fetchall()
            
            incentives = []
            for row in results:
                if row['requirements']:
                    try:
                        row['requirements'] = json.loads(row['requirements']) if isinstance(row['requirements'], str) else row['requirements']
                    except (json.JSONDecodeError, TypeError):
                        row['requirements'] = {}
                
                incentives.append(FilmIncentive(**row))
            
            logger.info(f"🎯 Found {len(incentives)} matching incentives for ${budget:,.0f} budget")
            return incentives
            
        except Error as e:
            logger.error(f"❌ Error finding matching incentives: {e}")
            return []

    def create_incentive(self, incentive: FilmIncentive) -> Optional[int]:
        """Create new film incentive"""
        try:
            cursor = self.get_connection().cursor()
            
            query = """
                INSERT INTO film_incentives (
                    country, region, incentive_type, percentage, max_credit,
                    requirements, application_deadline, current_cap_remaining,
                    is_active, minimum_spend, maximum_spend, processing_time_days,
                    expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            requirements_json = json.dumps(incentive.requirements) if incentive.requirements else None
            
            values = (
                incentive.country, incentive.region, incentive.incentive_type,
                incentive.percentage, incentive.max_credit, requirements_json,
                incentive.application_deadline, incentive.current_cap_remaining,
                incentive.is_active, incentive.minimum_spend, incentive.maximum_spend,
                incentive.processing_time_days, incentive.expires_at
            )
            
            cursor.execute(query, values)
            incentive_id = cursor.lastrowid
            
            logger.info(f"✅ Created incentive ID {incentive_id} for {incentive.country}")
            return incentive_id
            
        except Error as e:
            logger.error(f"❌ Error creating incentive: {e}")
            return None

    # ==================== LOCATION REQUIREMENT CRUD ====================
    
    def get_location_requirements(self, analysis_id: str) -> List[LocationRequirement]:
        """Get location requirements for an analysis"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            
            query = """
                SELECT id, analysis_id, location_type, description, script_mentions,
                       feasibility_score, estimated_days, special_requirements, created_at
                FROM location_requirements
                WHERE analysis_id = %s
                ORDER BY feasibility_score DESC, script_mentions DESC
            """
            
            cursor.execute(query, (analysis_id,))
            results = cursor.fetchall()
            
            requirements = []
            for row in results:
                if row['special_requirements']:
                    try:
                        row['special_requirements'] = json.loads(row['special_requirements']) if isinstance(row['special_requirements'], str) else row['special_requirements']
                    except (json.JSONDecodeError, TypeError):
                        row['special_requirements'] = {}
                
                requirements.append(LocationRequirement(**row))
            
            return requirements
            
        except Error as e:
            logger.error(f"❌ Error retrieving location requirements: {e}")
            return []

    def create_location_requirement(self, requirement: LocationRequirement) -> Optional[int]:
        """Create new location requirement"""
        try:
            cursor = self.get_connection().cursor()
            
            query = """
                INSERT INTO location_requirements (
                    analysis_id, location_type, description, script_mentions,
                    feasibility_score, estimated_days, special_requirements
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            special_req_json = json.dumps(requirement.special_requirements) if requirement.special_requirements else None
            
            values = (
                requirement.analysis_id, requirement.location_type, requirement.description,
                requirement.script_mentions, requirement.feasibility_score,
                requirement.estimated_days, special_req_json
            )
            
            cursor.execute(query, values)
            requirement_id = cursor.lastrowid
            
            logger.info(f"✅ Created location requirement ID {requirement_id}")
            return requirement_id
            
        except Error as e:
            logger.error(f"❌ Error creating location requirement: {e}")
            return None

    # ==================== ANALYSIS LOCATION MATCH CRUD ====================
    
    def create_incentive_match(self, match: AnalysisLocationMatch) -> Optional[int]:
        """Create new analysis-incentive match"""
        try:
            cursor = self.get_connection().cursor()
            
            query = """
                INSERT INTO analysis_location_matches (
                    analysis_id, incentive_id, location_requirement_id,
                    match_score, estimated_savings, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    match_score = VALUES(match_score),
                    estimated_savings = VALUES(estimated_savings),
                    notes = VALUES(notes)
            """
            
            values = (
                match.analysis_id, match.incentive_id, match.location_requirement_id,
                match.match_score, match.estimated_savings, match.notes
            )
            
            cursor.execute(query, values)
            match_id = cursor.lastrowid
            
            logger.info(f"✅ Created incentive match ID {match_id}")
            return match_id
            
        except Error as e:
            logger.error(f"❌ Error creating incentive match: {e}")
            return None

    def get_analysis_incentive_matches(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get incentive matches for an analysis with full incentive details"""
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            
            query = """
                SELECT 
                    alm.id as match_id,
                    alm.match_score,
                    alm.estimated_savings,
                    alm.notes,
                    fi.id as incentive_id,
                    fi.country,
                    fi.region,
                    fi.incentive_type,
                    fi.percentage,
                    fi.max_credit,
                    fi.minimum_spend,
                    fi.requirements,
                    lr.location_type,
                    lr.description as location_description
                FROM analysis_location_matches alm
                JOIN film_incentives fi ON alm.incentive_id = fi.id
                JOIN location_requirements lr ON alm.location_requirement_id = lr.id
                WHERE alm.analysis_id = %s
                ORDER BY alm.estimated_savings DESC, alm.match_score DESC
            """
            
            cursor.execute(query, (analysis_id,))
            results = cursor.fetchall()
            
            matches = []
            for row in results:
                if row['requirements']:
                    try:
                        row['requirements'] = json.loads(row['requirements']) if isinstance(row['requirements'], str) else row['requirements']
                    except (json.JSONDecodeError, TypeError):
                        row['requirements'] = {}
                
                matches.append(row)
            
            logger.info(f"📊 Retrieved {len(matches)} incentive matches for analysis {analysis_id}")
            return matches
            
        except Error as e:
            logger.error(f"❌ Error retrieving incentive matches: {e}")
            return []

    # ==================== UTILITY METHODS ====================
    
    def calculate_potential_savings(self, budget: float, incentives: List[FilmIncentive]) -> List[Dict[str, Any]]:
        """Calculate potential savings for a list of incentives"""
        savings_data = []
        
        for incentive in incentives:
            if not incentive.percentage:
                continue
            
            # Calculate qualifying spend
            qualifying_spend = budget
            if incentive.minimum_spend and budget < incentive.minimum_spend:
                continue  # Not eligible
            if incentive.maximum_spend and budget > incentive.maximum_spend:
                qualifying_spend = incentive.maximum_spend
            
            # Calculate savings (convert decimal to float for calculation)
            gross_savings = qualifying_spend * (float(incentive.percentage) / 100)
            
            # Apply max credit cap if exists (convert decimal to float)
            final_savings = gross_savings
            if incentive.max_credit and gross_savings > float(incentive.max_credit):
                final_savings = float(incentive.max_credit)
            
            # Calculate net production cost
            net_cost = budget - final_savings
            savings_percentage = (final_savings / budget) * 100
            
            savings_data.append({
                'incentive_id': incentive.id,
                'country': incentive.country,
                'region': incentive.region,
                'incentive_type': incentive.incentive_type,
                'percentage': incentive.percentage,
                'qualifying_spend': qualifying_spend,
                'gross_savings': gross_savings,
                'final_savings': final_savings,
                'net_production_cost': net_cost,
                'savings_percentage': savings_percentage,
                'max_credit_applied': incentive.max_credit and gross_savings > incentive.max_credit
            })
        
        # Sort by final savings descending
        savings_data.sort(key=lambda x: x['final_savings'], reverse=True)
        
        logger.info(f"💰 Calculated savings for {len(savings_data)} incentives")
        return savings_data

# ==================== SERVICE FUNCTIONS ====================

def get_incentive_service() -> IncentiveDatabase:
    """Get incentive database service instance"""
    return IncentiveDatabase()

def find_best_incentives_for_budget(budget: float, limit: int = 5) -> List[Dict[str, Any]]:
    """Find and calculate the best incentives for a given budget"""
    db = get_incentive_service()
    
    # Find matching incentives
    matching_incentives = db.find_matching_incentives(budget, min_percentage=15.0)
    
    # Calculate potential savings
    savings_data = db.calculate_potential_savings(budget, matching_incentives)
    
    # Return top results
    return savings_data[:limit]

def get_incentives_by_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get comprehensive incentive data for a specific analysis"""
    db = get_incentive_service()
    
    # Get location requirements
    locations = db.get_location_requirements(analysis_id)
    
    # Get incentive matches
    matches = db.get_analysis_incentive_matches(analysis_id)
    
    # Calculate totals
    total_savings = sum(match.get('estimated_savings', 0) for match in matches)
    
    return {
        'analysis_id': analysis_id,
        'location_requirements': [asdict(loc) for loc in locations],
        'incentive_matches': matches,
        'total_estimated_savings': total_savings,
        'matched_incentive_count': len(matches)
    }
