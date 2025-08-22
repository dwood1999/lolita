-- Recreate screenplay_analyses table with correct schema
-- This will ensure all fields match what the code expects

DROP TABLE IF EXISTS screenplay_analyses;

CREATE TABLE screenplay_analyses (
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
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_grok_confidence (grok_confidence)
);

-- Verify the table was created correctly
DESCRIBE screenplay_analyses;
