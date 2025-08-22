-- Add Phase 1 Grok Enhancement fields to screenplay_analyses table
-- Run this migration to support the new Grok cultural analysis features

ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_confidence DECIMAL(3,2);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_cultural_analysis JSON;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_brutal_honesty JSON;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS grok_controversy_analysis JSON;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_grok_confidence ON screenplay_analyses(grok_confidence);

-- Update existing records to have default values
UPDATE screenplay_analyses 
SET grok_confidence = 0.7 
WHERE grok_confidence IS NULL AND grok_score IS NOT NULL;

-- Verify the changes
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'screenplay_analyses' 
AND COLUMN_NAME LIKE 'grok_%'
ORDER BY COLUMN_NAME;
