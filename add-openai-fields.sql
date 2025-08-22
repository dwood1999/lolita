-- Add OpenAI analysis fields to screenplay_analyses table
-- Run this migration to add ChatGPT-4o support to existing databases

ALTER TABLE screenplay_analyses 
ADD COLUMN openai_score DECIMAL(3,1) AFTER grok_raw_response,
ADD COLUMN openai_recommendation VARCHAR(50) AFTER openai_score,
ADD COLUMN openai_verdict TEXT AFTER openai_recommendation,
ADD COLUMN openai_confidence DECIMAL(3,2) AFTER openai_verdict,
ADD COLUMN openai_commercial_assessment JSON AFTER openai_confidence,
ADD COLUMN openai_technical_craft JSON AFTER openai_commercial_assessment,
ADD COLUMN openai_industry_comparison JSON AFTER openai_technical_craft,
ADD COLUMN openai_raw_response LONGTEXT AFTER openai_industry_comparison;

-- Update api_costs table to track OpenAI usage
INSERT IGNORE INTO api_costs (user_id, analysis_id, api_provider, model_name, cost, processing_time, success, input_tokens, output_tokens, error_message, created_at)
SELECT 
    user_id, 
    id as analysis_id, 
    'openai' as api_provider, 
    'gpt-4o' as model_name, 
    0.0 as cost, 
    0.0 as processing_time, 
    1 as success, 
    0 as input_tokens, 
    0 as output_tokens, 
    NULL as error_message, 
    NOW() as created_at
FROM screenplay_analyses 
WHERE openai_score IS NOT NULL;

-- Add index for better query performance
CREATE INDEX idx_openai_score ON screenplay_analyses(openai_score);
CREATE INDEX idx_openai_recommendation ON screenplay_analyses(openai_recommendation);

SELECT 'OpenAI fields added successfully to screenplay_analyses table' as status;
