-- Add GPT-5 Writing Excellence Analysis fields to screenplay_analyses table

-- Core GPT-5 fields
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_score DECIMAL(3,1);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_recommendation VARCHAR(50);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_executive_assessment LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_reasoning_depth ENUM('quick', 'deep', 'hybrid', 'auto', 'fallback');
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_reasoning_tokens INT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_confidence DECIMAL(3,2);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_processing_time DECIMAL(8,2);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_cost DECIMAL(8,4);
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_raw_response LONGTEXT;

-- Writing Excellence Analysis fields (JSON)
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_character_voice_analysis LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_dialogue_authenticity LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_prose_quality LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_emotional_beat_mapping LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_professional_markers LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_amateur_indicators LONGTEXT;
ALTER TABLE screenplay_analyses ADD COLUMN IF NOT EXISTS gpt5_industry_comparison LONGTEXT;

-- Create index for GPT-5 score for performance
CREATE INDEX IF NOT EXISTS idx_gpt5_score ON screenplay_analyses(gpt5_score);

-- Verify the new fields were added
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'screenplay_analyses' 
AND COLUMN_NAME LIKE 'gpt5_%'
ORDER BY COLUMN_NAME;
