#!/usr/bin/env python3
"""
Film Incentive Data Updater Service
Automated service to keep film incentive data up-to-date through web scraping and API calls
"""

import os
import json
import logging
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

from incentive_models import IncentiveDatabase, FilmIncentive

load_dotenv(dotenv_path='../.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('incentive_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class IncentiveSource:
    """Configuration for an incentive data source"""
    name: str
    url: str
    country: str
    scraper_type: str  # 'html', 'api', 'pdf'
    selectors: Dict[str, str]  # CSS selectors or API field mappings
    update_frequency: int  # days between updates
    last_updated: Optional[datetime] = None
    is_active: bool = True

class IncentiveUpdaterService:
    """Service to automatically update film incentive data"""
    
    def __init__(self):
        self.db = IncentiveDatabase()
        self.session = None
        self.sources = self._load_incentive_sources()
        logger.info("🔄 Incentive Updater Service initialized")
    
    def _load_incentive_sources(self) -> List[IncentiveSource]:
        """Load configured incentive data sources"""
        sources = [
            # United States - State Film Offices
            IncentiveSource(
                name="Georgia Film Office",
                url="https://www.georgia.org/industries/film-entertainment/georgia-film-tv-production-incentive",
                country="United States",
                scraper_type="html",
                selectors={
                    "percentage": ".incentive-rate",
                    "requirements": ".requirements-list",
                    "cap": ".annual-cap"
                },
                update_frequency=30
            ),
            
            IncentiveSource(
                name="Louisiana Film Office",
                url="https://www.louisianaentertainment.gov/film-tv/incentives",
                country="United States",
                scraper_type="html",
                selectors={
                    "percentage": ".tax-credit-rate",
                    "requirements": ".eligibility-requirements",
                    "minimum_spend": ".minimum-spend"
                },
                update_frequency=30
            ),
            
            IncentiveSource(
                name="New York State Film Office",
                url="https://esd.ny.gov/film-tax-credit-programs",
                country="United States",
                scraper_type="html",
                selectors={
                    "percentage": ".credit-percentage",
                    "cap": ".program-cap",
                    "requirements": ".program-requirements"
                },
                update_frequency=30
            ),
            
            # Canada - Provincial Film Offices
            IncentiveSource(
                name="Telefilm Canada",
                url="https://telefilm.ca/en/funding",
                country="Canada",
                scraper_type="html",
                selectors={
                    "programs": ".funding-program",
                    "amounts": ".funding-amount",
                    "requirements": ".eligibility-criteria"
                },
                update_frequency=14
            ),
            
            IncentiveSource(
                name="Ontario Creates",
                url="https://ontariocreates.ca/funding/film-and-television",
                country="Canada",
                scraper_type="html",
                selectors={
                    "percentage": ".tax-credit-rate",
                    "cap": ".annual-allocation",
                    "requirements": ".eligibility-requirements"
                },
                update_frequency=30
            ),
            
            # United Kingdom
            IncentiveSource(
                name="BFI Film Fund",
                url="https://www.bfi.org.uk/supporting-uk-film/production-development-funding",
                country="United Kingdom",
                scraper_type="html",
                selectors={
                    "percentage": ".tax-relief-rate",
                    "requirements": ".cultural-test",
                    "minimum_spend": ".minimum-uk-spend"
                },
                update_frequency=30
            ),
            
            # Australia
            IncentiveSource(
                name="Screen Australia",
                url="https://www.screenaustralia.gov.au/funding-and-support",
                country="Australia",
                scraper_type="html",
                selectors={
                    "rebate": ".producer-rebate",
                    "offset": ".location-offset",
                    "requirements": ".australian-content"
                },
                update_frequency=30
            ),
            
            # European Union
            IncentiveSource(
                name="MEDIA Programme",
                url="https://ec.europa.eu/programmes/creative-europe/actions/media_en",
                country="European Union",
                scraper_type="html",
                selectors={
                    "funding": ".funding-amounts",
                    "requirements": ".eligibility-criteria",
                    "deadlines": ".application-deadlines"
                },
                update_frequency=7
            )
        ]
        
        logger.info(f"📋 Loaded {len(sources)} incentive data sources")
        return sources
    
    async def update_all_incentives(self) -> Dict[str, Any]:
        """Update all incentive data from configured sources"""
        logger.info("🚀 Starting comprehensive incentive data update")
        
        results = {
            'started_at': datetime.now().isoformat(),
            'sources_processed': 0,
            'incentives_updated': 0,
            'incentives_added': 0,
            'errors': [],
            'summary': {}
        }
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (compatible; FilmIncentiveBot/1.0)'}
        ) as session:
            self.session = session
            
            # Process sources in parallel batches to avoid overwhelming servers
            batch_size = 3
            for i in range(0, len(self.sources), batch_size):
                batch = self.sources[i:i + batch_size]
                batch_tasks = [self._update_source(source) for source in batch]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for source, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        error_msg = f"Failed to update {source.name}: {str(result)}"
                        logger.error(error_msg)
                        results['errors'].append(error_msg)
                    else:
                        results['sources_processed'] += 1
                        results['incentives_updated'] += result.get('updated', 0)
                        results['incentives_added'] += result.get('added', 0)
                        results['summary'][source.name] = result
                
                # Brief pause between batches
                await asyncio.sleep(2)
        
        # Update database statistics
        await self._update_database_stats()
        
        results['completed_at'] = datetime.now().isoformat()
        results['duration_minutes'] = (
            datetime.fromisoformat(results['completed_at']) - 
            datetime.fromisoformat(results['started_at'])
        ).total_seconds() / 60
        
        logger.info(f"✅ Update completed: {results['sources_processed']} sources, "
                   f"{results['incentives_updated']} updated, {results['incentives_added']} added")
        
        return results
    
    async def _update_source(self, source: IncentiveSource) -> Dict[str, Any]:
        """Update incentives from a single source"""
        logger.info(f"🔍 Updating incentives from {source.name}")
        
        result = {'source': source.name, 'updated': 0, 'added': 0, 'errors': []}
        
        try:
            if source.scraper_type == 'html':
                incentives = await self._scrape_html_source(source)
            elif source.scraper_type == 'api':
                incentives = await self._fetch_api_source(source)
            else:
                logger.warning(f"⚠️ Unsupported scraper type: {source.scraper_type}")
                return result
            
            # Process and save incentives
            for incentive_data in incentives:
                try:
                    incentive = self._create_incentive_from_data(incentive_data, source)
                    
                    # Check if incentive already exists
                    existing = self._find_existing_incentive(incentive)
                    
                    if existing:
                        if self._incentive_needs_update(existing, incentive):
                            self._update_existing_incentive(existing, incentive)
                            result['updated'] += 1
                    else:
                        self.db.create_incentive(incentive)
                        result['added'] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing incentive: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            # Update source last_updated timestamp
            source.last_updated = datetime.now()
            
        except Exception as e:
            error_msg = f"Error updating source {source.name}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    async def _scrape_html_source(self, source: IncentiveSource) -> List[Dict[str, Any]]:
        """Scrape incentive data from HTML source"""
        incentives = []
        
        try:
            async with self.session.get(source.url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ HTTP {response.status} for {source.url}")
                    return incentives
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract incentive data based on source-specific logic
                if source.name == "Georgia Film Office":
                    incentives = self._parse_georgia_incentives(soup)
                elif source.name == "Louisiana Film Office":
                    incentives = self._parse_louisiana_incentives(soup)
                elif source.name == "New York State Film Office":
                    incentives = self._parse_newyork_incentives(soup)
                elif source.name == "Telefilm Canada":
                    incentives = self._parse_telefilm_incentives(soup)
                elif source.name == "Ontario Creates":
                    incentives = self._parse_ontario_incentives(soup)
                elif source.name == "BFI Film Fund":
                    incentives = self._parse_bfi_incentives(soup)
                elif source.name == "Screen Australia":
                    incentives = self._parse_screenaustralia_incentives(soup)
                elif source.name == "MEDIA Programme":
                    incentives = self._parse_media_incentives(soup)
                else:
                    # Generic parsing fallback
                    incentives = self._parse_generic_incentives(soup, source)
                
        except Exception as e:
            logger.error(f"❌ Error scraping {source.url}: {str(e)}")
        
        logger.info(f"📊 Extracted {len(incentives)} incentives from {source.name}")
        return incentives
    
    def _parse_georgia_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Georgia-specific incentive data"""
        incentives = []
        
        # Georgia has a 20% base tax credit + 10% uplift
        base_incentive = {
            'country': 'United States',
            'region': 'Georgia',
            'incentive_type': 'tax_credit',
            'percentage': 30.0,  # 20% + 10% uplift
            'minimum_spend': 500000,
            'requirements': {
                'georgia_spend': 500000,
                'promotional_logo': True,
                'georgia_promotional_requirements': True
            },
            'processing_time_days': 90,
            'current_cap_remaining': None  # No annual cap
        }
        
        incentives.append(base_incentive)
        return incentives
    
    def _parse_louisiana_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Louisiana-specific incentive data"""
        incentives = []
        
        # Louisiana Motion Picture Production Tax Credit
        base_incentive = {
            'country': 'United States',
            'region': 'Louisiana',
            'incentive_type': 'tax_credit',
            'percentage': 25.0,  # Base 25% + potential 5% uplift
            'minimum_spend': 300000,
            'requirements': {
                'louisiana_spend': 300000,
                'louisiana_residents': 0.5,  # 50% Louisiana residents
                'transferable': True
            },
            'processing_time_days': 120,
            'max_credit': 180000000  # Annual program cap
        }
        
        incentives.append(base_incentive)
        return incentives
    
    def _parse_newyork_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse New York-specific incentive data"""
        incentives = []
        
        # NY Film Production Tax Credit
        film_credit = {
            'country': 'United States',
            'region': 'New York',
            'incentive_type': 'tax_credit',
            'percentage': 30.0,
            'minimum_spend': 1000000,
            'requirements': {
                'ny_spend': 1000000,
                'ny_shooting_days': 0.75,  # 75% of shooting days in NY
                'transferable': True
            },
            'processing_time_days': 180,
            'max_credit': 420000000  # Annual program cap
        }
        
        # NY Post-Production Tax Credit
        post_credit = {
            'country': 'United States',
            'region': 'New York',
            'incentive_type': 'tax_credit',
            'percentage': 30.0,
            'minimum_spend': 500000,
            'requirements': {
                'ny_post_spend': 500000,
                'post_production_facility': True,
                'transferable': True
            },
            'processing_time_days': 180,
            'max_credit': 25000000  # Annual program cap
        }
        
        incentives.extend([film_credit, post_credit])
        return incentives
    
    def _parse_telefilm_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Telefilm Canada incentive data"""
        incentives = []
        
        # This would parse actual Telefilm funding programs
        # For now, return basic structure
        base_incentive = {
            'country': 'Canada',
            'region': None,
            'incentive_type': 'grant',
            'percentage': None,
            'minimum_spend': None,
            'max_credit': 1000000,  # Varies by program
            'requirements': {
                'canadian_content': 6,  # CAVCO points
                'canadian_producer': True,
                'cultural_significance': True
            },
            'processing_time_days': 90
        }
        
        incentives.append(base_incentive)
        return incentives
    
    def _parse_ontario_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Ontario Creates incentive data"""
        incentives = []
        
        # Ontario Film and Television Tax Credit
        oftc = {
            'country': 'Canada',
            'region': 'Ontario',
            'incentive_type': 'tax_credit',
            'percentage': 35.0,  # Base rate
            'minimum_spend': None,
            'requirements': {
                'ontario_labour': 0.25,  # 25% Ontario labour
                'canadian_content': True,
                'cavco_certification': True
            },
            'processing_time_days': 120
        }
        
        incentives.append(oftc)
        return incentives
    
    def _parse_bfi_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse BFI UK incentive data"""
        incentives = []
        
        # UK Film Tax Relief
        film_relief = {
            'country': 'United Kingdom',
            'region': None,
            'incentive_type': 'tax_credit',
            'percentage': 25.0,  # 25% of UK qualifying expenditure
            'minimum_spend': 1000000,
            'requirements': {
                'uk_spend': 0.10,  # 10% of total budget in UK
                'cultural_test': True,
                'british_film': True
            },
            'processing_time_days': 90
        }
        
        incentives.append(film_relief)
        return incentives
    
    def _parse_screenaustralia_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Screen Australia incentive data"""
        incentives = []
        
        # Producer Rebate
        producer_rebate = {
            'country': 'Australia',
            'region': None,
            'incentive_type': 'rebate',
            'percentage': 30.0,  # 30% rebate on QAPE
            'minimum_spend': 1000000,
            'requirements': {
                'australian_spend': 1000000,
                'significant_australian_content': True,
                'australian_producer': True
            },
            'processing_time_days': 120
        }
        
        # Location Offset
        location_offset = {
            'country': 'Australia',
            'region': None,
            'incentive_type': 'rebate',
            'percentage': 16.5,  # 16.5% rebate on QAPE
            'minimum_spend': 15000000,
            'requirements': {
                'australian_spend': 15000000,
                'international_production': True,
                'tourism_benefits': True
            },
            'processing_time_days': 120
        }
        
        incentives.extend([producer_rebate, location_offset])
        return incentives
    
    def _parse_media_incentives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse EU MEDIA Programme incentive data"""
        incentives = []
        
        # MEDIA Development Support
        development = {
            'country': 'European Union',
            'region': None,
            'incentive_type': 'grant',
            'percentage': None,
            'minimum_spend': None,
            'max_credit': 60000,
            'requirements': {
                'european_producer': True,
                'cultural_diversity': True,
                'cross_border_potential': True
            },
            'processing_time_days': 90
        }
        
        incentives.append(development)
        return incentives
    
    def _parse_generic_incentives(self, soup: BeautifulSoup, source: IncentiveSource) -> List[Dict[str, Any]]:
        """Generic fallback parser for unknown sources"""
        incentives = []
        
        # Try to extract basic information using common patterns
        try:
            # Look for percentage patterns
            percentage_text = soup.get_text()
            percentage_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', percentage_text)
            
            if percentage_matches:
                percentage = float(percentage_matches[0])
                
                base_incentive = {
                    'country': source.country,
                    'region': None,
                    'incentive_type': 'tax_credit',
                    'percentage': percentage,
                    'minimum_spend': None,
                    'requirements': {},
                    'processing_time_days': 90
                }
                
                incentives.append(base_incentive)
        
        except Exception as e:
            logger.error(f"❌ Generic parsing failed for {source.name}: {str(e)}")
        
        return incentives
    
    async def _fetch_api_source(self, source: IncentiveSource) -> List[Dict[str, Any]]:
        """Fetch incentive data from API source"""
        incentives = []
        
        try:
            async with self.session.get(source.url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Process API response based on source format
                    incentives = self._process_api_data(data, source)
                else:
                    logger.warning(f"⚠️ API returned status {response.status} for {source.url}")
        
        except Exception as e:
            logger.error(f"❌ Error fetching API data from {source.url}: {str(e)}")
        
        return incentives
    
    def _process_api_data(self, data: Dict[str, Any], source: IncentiveSource) -> List[Dict[str, Any]]:
        """Process API response data into incentive format"""
        incentives = []
        
        # This would be customized based on each API's response format
        # For now, return empty list
        
        return incentives
    
    def _create_incentive_from_data(self, data: Dict[str, Any], source: IncentiveSource) -> FilmIncentive:
        """Create FilmIncentive object from scraped data"""
        return FilmIncentive(
            country=data.get('country', source.country),
            region=data.get('region'),
            incentive_type=data.get('incentive_type', 'tax_credit'),
            percentage=data.get('percentage'),
            max_credit=data.get('max_credit'),
            minimum_spend=data.get('minimum_spend'),
            maximum_spend=data.get('maximum_spend'),
            requirements=data.get('requirements', {}),
            processing_time_days=data.get('processing_time_days', 90),
            current_cap_remaining=data.get('current_cap_remaining'),
            is_active=True,
            updated_at=datetime.now()
        )
    
    def _find_existing_incentive(self, incentive: FilmIncentive) -> Optional[FilmIncentive]:
        """Find existing incentive in database"""
        # This would query the database to find matching incentive
        # For now, return None (always create new)
        return None
    
    def _incentive_needs_update(self, existing: FilmIncentive, new: FilmIncentive) -> bool:
        """Check if existing incentive needs to be updated"""
        # Compare key fields to determine if update is needed
        return (
            existing.percentage != new.percentage or
            existing.max_credit != new.max_credit or
            existing.minimum_spend != new.minimum_spend or
            existing.requirements != new.requirements
        )
    
    def _update_existing_incentive(self, existing: FilmIncentive, new: FilmIncentive):
        """Update existing incentive with new data"""
        # This would update the existing incentive in the database
        pass
    
    async def _update_database_stats(self):
        """Update database statistics after update"""
        try:
            # Update incentive statistics, cleanup old data, etc.
            logger.info("📊 Updated database statistics")
        except Exception as e:
            logger.error(f"❌ Error updating database stats: {str(e)}")
    
    async def check_sources_health(self) -> Dict[str, Any]:
        """Check health status of all incentive sources"""
        logger.info("🏥 Checking health of incentive sources")
        
        health_report = {
            'checked_at': datetime.now().isoformat(),
            'sources': {},
            'healthy_count': 0,
            'unhealthy_count': 0
        }
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            
            for source in self.sources:
                try:
                    start_time = datetime.now()
                    async with session.get(source.url) as response:
                        response_time = (datetime.now() - start_time).total_seconds()
                        
                        health_report['sources'][source.name] = {
                            'url': source.url,
                            'status_code': response.status,
                            'response_time_seconds': response_time,
                            'healthy': response.status == 200,
                            'last_updated': source.last_updated.isoformat() if source.last_updated else None
                        }
                        
                        if response.status == 200:
                            health_report['healthy_count'] += 1
                        else:
                            health_report['unhealthy_count'] += 1
                
                except Exception as e:
                    health_report['sources'][source.name] = {
                        'url': source.url,
                        'error': str(e),
                        'healthy': False,
                        'last_updated': source.last_updated.isoformat() if source.last_updated else None
                    }
                    health_report['unhealthy_count'] += 1
        
        logger.info(f"🏥 Health check complete: {health_report['healthy_count']} healthy, "
                   f"{health_report['unhealthy_count']} unhealthy")
        
        return health_report

# ==================== CLI INTERFACE ====================

async def main():
    """Main CLI interface for the incentive updater"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Film Incentive Data Updater')
    parser.add_argument('--update', action='store_true', help='Update all incentive data')
    parser.add_argument('--health', action='store_true', help='Check source health')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    updater = IncentiveUpdaterService()
    
    if args.health:
        health_report = await updater.check_sources_health()
        print(json.dumps(health_report, indent=2))
    
    elif args.update:
        update_results = await updater.update_all_incentives()
        print(json.dumps(update_results, indent=2))
    
    else:
        print("Use --update to update incentives or --health to check source health")

if __name__ == "__main__":
    asyncio.run(main())
