-- Film Incentive Tracking Migration
-- Adds comprehensive film incentive and location tracking to support financial analysis
-- Compatible with existing lolita database structure

-- 1. Film Incentives Table
-- Tracks global film incentives, tax credits, and rebates by region
CREATE TABLE film_incentives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),                        -- State/Province/Territory
    incentive_type ENUM('tax_credit', 'rebate', 'grant', 'loan', 'infrastructure', 'service_credit') NOT NULL,
    percentage DECIMAL(5,2),                    -- Incentive percentage (e.g., 25.00 for 25%)
    max_credit DECIMAL(12,2),                   -- Maximum credit amount in USD
    requirements JSON,                          -- JSON object with eligibility requirements
    application_deadline DATE,                  -- Annual deadline (recurring)
    current_cap_remaining DECIMAL(12,2),        -- Remaining budget for the program
    is_active BOOLEAN DEFAULT TRUE,
    minimum_spend DECIMAL(12,2),                -- Minimum local spend required
    maximum_spend DECIMAL(12,2),                -- Maximum qualifying spend
    processing_time_days INT,                   -- Typical processing time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,                  -- When this incentive program expires
    
    INDEX idx_country_region (country, region),
    INDEX idx_incentive_type (incentive_type),
    INDEX idx_active_incentives (is_active, expires_at),
    INDEX idx_percentage (percentage)
);

-- 2. Location Requirements Table  
-- Links screenplay analysis to location requirements and feasibility
CREATE TABLE location_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(255) NOT NULL,          -- Links to screenplay_analyses.id
    location_type ENUM('primary', 'secondary', 'studio', 'exterior', 'interior', 'special') NOT NULL,
    description TEXT NOT NULL,                  -- What type of location is needed
    script_mentions INT DEFAULT 0,              -- How many times mentioned in script
    feasibility_score DECIMAL(3,1),            -- 0-10 score for filming feasibility
    estimated_days INT,                         -- Estimated filming days at this location
    special_requirements JSON,                  -- Special needs (permits, equipment, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_location_type (location_type),
    INDEX idx_feasibility_score (feasibility_score),
    FOREIGN KEY (analysis_id) REFERENCES screenplay_analyses(id) ON DELETE CASCADE
);

-- 3. Analysis Location Matches Table
-- Links screenplay location requirements to available incentives  
CREATE TABLE analysis_location_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id VARCHAR(255) NOT NULL,
    incentive_id INT NOT NULL,
    location_requirement_id INT NOT NULL,
    match_score DECIMAL(3,1),                   -- 0-10 how good this match is
    estimated_savings DECIMAL(12,2),            -- Projected savings from this incentive
    notes TEXT,                                 -- Additional considerations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_match_score (match_score),
    INDEX idx_estimated_savings (estimated_savings),
    FOREIGN KEY (analysis_id) REFERENCES screenplay_analyses(id) ON DELETE CASCADE,
    FOREIGN KEY (incentive_id) REFERENCES film_incentives(id) ON DELETE CASCADE,
    FOREIGN KEY (location_requirement_id) REFERENCES location_requirements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_analysis_incentive_location (analysis_id, incentive_id, location_requirement_id)
);

-- 4. Insert Sample Film Incentives Data
-- Popular film incentives to get started
INSERT INTO film_incentives (country, region, incentive_type, percentage, max_credit, requirements, application_deadline, current_cap_remaining, minimum_spend, maximum_spend, processing_time_days) VALUES
-- United States
('United States', 'Georgia', 'tax_credit', 30.00, NULL, '{"local_crew_requirement": 75, "georgia_spend_minimum": 500000, "qualified_expenses": ["below_line", "equipment", "locations"]}', '2024-12-31', 1000000000.00, 500000.00, NULL, 45),
('United States', 'Louisiana', 'tax_credit', 25.00, 180000000.00, '{"local_spend_requirement": 300000, "transferable": true, "qualified_expenses": ["payroll", "goods", "services"]}', '2024-12-31', 150000000.00, 300000.00, NULL, 60),
('United States', 'New Mexico', 'rebate', 35.00, 50000000.00, '{"resident_workers": 60, "new_mexico_spend": 1000000, "qualified_expenses": ["crew", "equipment", "locations"]}', '2024-12-31', 110000000.00, 1000000.00, NULL, 30),
('United States', 'New York', 'tax_credit', 30.00, 420000000.00, '{"upstate_bonus": 10, "nyc_qualified": true, "minimum_spend": 1000000}', '2024-12-31', 200000000.00, 1000000.00, NULL, 75),
('United States', 'California', 'tax_credit', 25.00, 330000000.00, '{"ca_spend_requirement": 1000000, "jobs_ratio": 75, "independent_films": true}', '2024-12-31', 180000000.00, 1000000.00, NULL, 90),

-- Canada  
('Canada', 'British Columbia', 'tax_credit', 35.00, NULL, '{"bc_labour": 75, "canadian_content": true, "minimum_spend": 1000000}', '2024-12-31', 500000000.00, 1000000.00, NULL, 45),
('Canada', 'Ontario', 'tax_credit', 35.00, NULL, '{"ontario_spend": 1000000, "canadian_content": 75, "labour_requirement": true}', '2024-12-31', 267000000.00, 1000000.00, NULL, 60),
('Canada', 'Quebec', 'tax_credit', 35.00, NULL, '{"quebec_labour": 75, "french_content_bonus": 10, "minimum_spend": 1000000}', '2024-12-31', 200000000.00, 1000000.00, NULL, 45),

-- United Kingdom
('United Kingdom', 'England', 'tax_credit', 25.00, NULL, '{"uk_spend": 10000000, "cultural_test": true, "european_withholding": 0}', '2024-12-31', 500000000.00, 1000000.00, NULL, 30),
('United Kingdom', 'Northern Ireland', 'rebate', 25.00, NULL, '{"ni_spend": 500000, "uk_cultural_test": true, "local_crew": 50}', '2024-12-31', 100000000.00, 500000.00, NULL, 45),

-- Australia
('Australia', 'New South Wales', 'rebate', 30.00, NULL, '{"nsw_spend": 15000000, "australian_content": true, "post_production": 500000}', '2024-12-31', 175000000.00, 15000000.00, NULL, 60),
('Australia', 'Victoria', 'rebate', 25.00, NULL, '{"vic_spend": 2000000, "australian_content": 65, "local_crew": 70}', '2024-12-31', 191600000.00, 2000000.00, NULL, 45),

-- Other Popular Destinations
('Ireland', NULL, 'tax_credit', 32.00, NULL, '{"irish_spend": 125000, "european_content": true, "cultural_test": true}', '2024-12-31', 125000000.00, 125000.00, NULL, 45),
('Czech Republic', NULL, 'rebate', 30.00, NULL, '{"czech_spend": 1000000, "european_content": 70, "cultural_significance": true}', '2024-12-31', 31000000.00, 1000000.00, NULL, 60),
('South Africa', NULL, 'rebate', 25.00, NULL, '{"sa_spend": 2500000, "local_spend": 50, "qspe_qualified": true}', '2024-12-31', 47000000.00, 2500000.00, NULL, 90);

-- 5. Add indexes for performance optimization
CREATE INDEX idx_incentives_performance ON film_incentives(country, is_active, percentage DESC);
CREATE INDEX idx_location_analysis ON location_requirements(analysis_id, feasibility_score DESC);
CREATE INDEX idx_matches_performance ON analysis_location_matches(analysis_id, match_score DESC, estimated_savings DESC);

-- 6. Add new columns to existing screenplay_analyses table for incentive integration
ALTER TABLE screenplay_analyses 
ADD COLUMN incentive_analysis_complete BOOLEAN DEFAULT FALSE,
ADD COLUMN total_estimated_incentives DECIMAL(12,2) DEFAULT 0.00,
ADD COLUMN recommended_filming_locations JSON,
ADD COLUMN incentive_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 7. Create view for easy incentive reporting
CREATE VIEW v_active_incentives AS
SELECT 
    fi.id,
    fi.country,
    fi.region,
    fi.incentive_type,
    fi.percentage,
    fi.max_credit,
    fi.minimum_spend,
    fi.current_cap_remaining,
    fi.processing_time_days,
    CASE 
        WHEN fi.current_cap_remaining > fi.minimum_spend THEN 'Available'
        WHEN fi.current_cap_remaining > 0 THEN 'Limited'
        ELSE 'Full'
    END as availability_status
FROM film_incentives fi
WHERE fi.is_active = TRUE 
AND (fi.expires_at IS NULL OR fi.expires_at > NOW())
ORDER BY fi.percentage DESC;

-- 8. Create view for analysis with location matches
CREATE VIEW v_analysis_incentive_summary AS
SELECT 
    sa.analysis_id,
    sa.title,
    sa.genre,
    COUNT(DISTINCT alm.incentive_id) as matched_incentives,
    SUM(alm.estimated_savings) as total_estimated_savings,
    AVG(alm.match_score) as avg_match_score,
    sa.total_estimated_incentives,
    sa.incentive_analysis_complete
FROM screenplay_analyses sa
LEFT JOIN analysis_location_matches alm ON sa.analysis_id = alm.analysis_id
GROUP BY sa.analysis_id, sa.title, sa.genre, sa.total_estimated_incentives, sa.incentive_analysis_complete;
