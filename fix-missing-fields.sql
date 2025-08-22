-- Fix missing fields in screenplay_analyses table
-- This ensures all fields referenced in the code actually exist

-- Add missing basic fields
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS subgenre VARCHAR(100);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS logline TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS director_recommendation TEXT;

-- Verify all Grok Phase 1 fields exist (these should already be there from previous migration)
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_score DECIMAL(3,1);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_recommendation VARCHAR(50);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_verdict TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_confidence DECIMAL(3,2);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_cultural_analysis JSON;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_brutal_honesty JSON;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_controversy_analysis JSON;

-- Verify the table structure
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'screenplay_analyses' 
AND (COLUMN_NAME LIKE '%grok%' OR COLUMN_NAME IN ('subgenre', 'logline', 'director_recommendation'))
ORDER BY COLUMN_NAME;

-- Add missing Phase 2 poster fields if not present
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_movie_poster_url TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_poster_prompt TEXT;
