-- Add source material analysis fields to screenplay_analyses table
-- Migration: Add source material detection and analysis fields

ALTER TABLE screenplay_analyses ADD COLUMN source_has_material BOOLEAN DEFAULT FALSE;
ALTER TABLE screenplay_analyses ADD COLUMN source_type VARCHAR(50);
ALTER TABLE screenplay_analyses ADD COLUMN source_title TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_author VARCHAR(255);
ALTER TABLE screenplay_analyses ADD COLUMN source_description TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_adaptation_notes TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_commercial_implications TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_legal_considerations TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_market_advantages JSON;
ALTER TABLE screenplay_analyses ADD COLUMN source_potential_challenges JSON;
ALTER TABLE screenplay_analyses ADD COLUMN source_confidence_score DECIMAL(3,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN source_raw_detection_text TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN source_processing_time DECIMAL(8,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN source_cost DECIMAL(8,4) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN source_success BOOLEAN DEFAULT FALSE;
ALTER TABLE screenplay_analyses ADD COLUMN source_error_message TEXT;

-- Add indexes for better query performance
CREATE INDEX idx_screenplay_analyses_source_has_material ON screenplay_analyses(source_has_material);
CREATE INDEX idx_screenplay_analyses_source_type ON screenplay_analyses(source_type);
CREATE INDEX idx_screenplay_analyses_source_success ON screenplay_analyses(source_success);
