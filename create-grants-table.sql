-- Film Grants and Awards Table Creation
-- Comprehensive database for film grants, awards, and funding opportunities

CREATE TABLE IF NOT EXISTS film_grants_awards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    grant_type ENUM('development', 'production', 'post_production', 'distribution', 'festival', 'emerging_filmmaker', 'diversity', 'documentary', 'short_film', 'feature_film') NOT NULL,
    amount_min DECIMAL(12,2),
    amount_max DECIMAL(12,2),
    eligibility_requirements JSON,
    application_deadline DATE,
    application_frequency ENUM('annual', 'biannual', 'quarterly', 'rolling', 'one_time') DEFAULT 'annual',
    target_demographics JSON,
    genre_focus JSON,
    website_url VARCHAR(500),
    success_rate_percentage DECIMAL(5,2),
    average_award_amount DECIMAL(12,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_country_region (country, region),
    INDEX idx_grant_type (grant_type),
    INDEX idx_active_grants (is_active),
    INDEX idx_amount (average_award_amount DESC)
);

-- Insert sample grants data
INSERT INTO film_grants_awards (
    name, organization, country, region, grant_type, amount_min, amount_max, 
    eligibility_requirements, application_deadline, application_frequency, 
    target_demographics, genre_focus, website_url, success_rate_percentage, 
    average_award_amount, is_active
) VALUES 

-- United States Grants
('Sundance Institute Documentary Fund', 'Sundance Institute', 'United States', NULL, 'documentary', 15000.00, 50000.00, 
'{"project_stage": "development_or_production", "first_time_filmmaker": false, "social_impact": true}', 
'2024-09-15', 'annual', '["independent_filmmakers", "documentary_makers"]', '["documentary", "social_issue"]', 
'https://www.sundance.org/programs/documentary-fund', 15.5, 35000.00, TRUE),

('Cinereach Grants', 'Cinereach', 'United States', NULL, 'production', 10000.00, 75000.00,
'{"narrative_focus": true, "innovative_storytelling": true, "underrepresented_voices": true}',
'2024-11-01', 'biannual', '["emerging_filmmakers", "underrepresented_voices"]', '["narrative", "experimental"]',
'https://cinereach.org/grants/', 12.3, 42000.00, TRUE),

('Chicken & Egg Pictures', 'Chicken & Egg Pictures', 'United States', NULL, 'development', 5000.00, 25000.00,
'{"women_directors": true, "documentary_focus": true, "social_impact": true}',
'2024-08-30', 'annual', '["women_filmmakers"]', '["documentary", "social_issue"]',
'https://chickeneggpics.org/', 18.7, 15000.00, TRUE),

('NEA Media Arts Fellowships', 'National Endowment for the Arts', 'United States', NULL, 'development', 25000.00, 25000.00,
'{"us_citizen": true, "artistic_excellence": true, "individual_artist": true}',
'2024-07-15', 'annual', '["individual_artists"]', '["all_genres"]',
'https://www.arts.gov/grants/apply-grant/grants-individuals', 8.2, 25000.00, TRUE),

-- Canada Grants
('Telefilm Canada Micro-Budget Production Program', 'Telefilm Canada', 'Canada', NULL, 'production', 125000.00, 250000.00,
'{"canadian_content": true, "budget_under_250k": true, "first_or_second_feature": true}',
'2024-12-01', 'rolling', '["canadian_filmmakers", "emerging_filmmakers"]', '["narrative", "feature_film"]',
'https://telefilm.ca/en/funding/production-funding', 25.4, 187500.00, TRUE),

('Canada Council for the Arts', 'Canada Council for the Arts', 'Canada', NULL, 'development', 5000.00, 60000.00,
'{"canadian_citizen": true, "artistic_merit": true, "professional_development": true}',
'2024-10-15', 'annual', '["canadian_artists"]', '["all_genres"]',
'https://canadacouncil.ca/funding/grants', 22.1, 32500.00, TRUE),

('Ontario Creates Film Fund', 'Ontario Creates', 'Canada', 'Ontario', 'production', 50000.00, 500000.00,
'{"ontario_production": true, "canadian_content": 6, "cultural_significance": true}',
'2024-09-30', 'quarterly', '["ontario_filmmakers"]', '["narrative", "documentary"]',
'https://ontariocreates.ca/funding/film-and-television', 35.2, 275000.00, TRUE),

-- United Kingdom Grants
('BFI Doc Society Fund', 'British Film Institute', 'United Kingdom', NULL, 'documentary', 15000.00, 80000.00,
'{"social_impact": true, "creative_excellence": true, "uk_connection": true}',
'2024-11-15', 'quarterly', '["documentary_makers", "social_impact_filmmakers"]', '["documentary", "social_issue"]',
'https://www.bfi.org.uk/supporting-uk-film/production-development-funding', 28.3, 47500.00, TRUE),

('Creative England iFeatures', 'Creative England', 'United Kingdom', NULL, 'production', 150000.00, 300000.00,
'{"uk_based": true, "innovative_approach": true, "commercial_potential": true}',
'2024-08-01', 'annual', '["uk_filmmakers", "emerging_filmmakers"]', '["narrative", "innovative"]',
'https://creativeengland.co.uk/film-funding/', 15.8, 225000.00, TRUE),

-- European Grants
('MEDIA Programme', 'European Commission', 'European Union', NULL, 'development', 25000.00, 60000.00,
'{"european_content": true, "cultural_diversity": true, "cross_border_collaboration": true}',
'2024-10-01', 'annual', '["european_filmmakers"]', '["all_genres"]',
'https://ec.europa.eu/programmes/creative-europe/actions/media_en', 31.7, 42500.00, TRUE),

('Eurimages', 'Council of Europe', 'European Union', NULL, 'production', 100000.00, 500000.00,
'{"european_coproduction": true, "cultural_significance": true, "artistic_quality": true}',
'2024-09-15', 'quarterly', '["european_coproducers"]', '["narrative", "documentary"]',
'https://www.coe.int/en/web/eurimages', 18.9, 300000.00, TRUE),

-- Australia Grants
('Screen Australia Documentary Producer Program', 'Screen Australia', 'Australia', NULL, 'documentary', 20000.00, 100000.00,
'{"australian_content": true, "cultural_significance": true, "audience_appeal": true}',
'2024-11-30', 'rolling', '["australian_filmmakers"]', '["documentary"]',
'https://www.screenaustralia.gov.au/funding-and-support/documentary/producer-program', 24.6, 60000.00, TRUE),

-- Diversity and Inclusion Focused Grants
('Sundance Indigenous Program', 'Sundance Institute', 'United States', NULL, 'development', 10000.00, 40000.00,
'{"indigenous_filmmaker": true, "authentic_storytelling": true, "cultural_preservation": true}',
'2024-08-15', 'annual', '["indigenous_filmmakers"]', '["all_genres"]',
'https://www.sundance.org/programs/indigenous-program', 22.4, 25000.00, TRUE),

('Perspective Fund', 'Perspective Fund', 'United States', NULL, 'production', 25000.00, 100000.00,
'{"women_directors": true, "underrepresented_voices": true, "narrative_feature": true}',
'2024-12-15', 'annual', '["women_filmmakers", "underrepresented_voices"]', '["narrative", "feature_film"]',
'https://www.perspectivefund.com/', 16.3, 62500.00, TRUE),

-- International/Global Grants
('Hubert Bals Fund', 'International Film Festival Rotterdam', 'Netherlands', NULL, 'development', 10000.00, 30000.00,
'{"innovative_cinema": true, "developing_countries": true, "artistic_vision": true}',
'2024-09-01', 'annual', '["international_filmmakers", "developing_countries"]', '["art_house", "experimental"]',
'https://iffr.com/en/professionals/hubert-bals-fund', 19.7, 20000.00, TRUE),

('Berlinale World Cinema Fund', 'Berlin International Film Festival', 'Germany', NULL, 'production', 15000.00, 70000.00,
'{"cultural_diversity": true, "artistic_innovation": true, "international_coproduction": true}',
'2024-10-31', 'annual', '["international_filmmakers"]', '["art_house", "cultural"]',
'https://www.berlinale.de/en/industry/world-cinema-fund/', 21.8, 42500.00, TRUE);

-- Create indexes for performance
CREATE INDEX idx_grants_performance ON film_grants_awards(country, grant_type, is_active, average_award_amount DESC);
CREATE INDEX idx_grants_deadline ON film_grants_awards(application_deadline, is_active);
CREATE INDEX idx_grants_amount ON film_grants_awards(amount_min, amount_max, is_active);
