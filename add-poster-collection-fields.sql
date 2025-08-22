-- Add poster collection fields to screenplay_analyses table
-- Migration: Add enhanced poster generation fields

ALTER TABLE screenplay_analyses ADD COLUMN poster_collection_title TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN poster_collection_genre TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN poster_total_cost DECIMAL(8,4) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN poster_total_time DECIMAL(8,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN poster_success_count INTEGER DEFAULT 0;
ALTER TABLE screenplay_analyses ADD COLUMN poster_best_url TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN poster_best_source TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN poster_variations_json TEXT;

-- Add individual poster source fields for backward compatibility
ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_url TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_prompt TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_cost DECIMAL(8,4) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_success BOOLEAN DEFAULT FALSE;
ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_error TEXT;

-- Add indexes for better query performance
CREATE INDEX idx_screenplay_analyses_poster_success ON screenplay_analyses(poster_success_count);
CREATE INDEX idx_screenplay_analyses_poster_source ON screenplay_analyses(poster_best_source);
CREATE INDEX idx_screenplay_analyses_flux_success ON screenplay_analyses(flux_poster_success);
