-- Fix column size issues for AI analysis results
-- The grok_recommendation column is too small (VARCHAR(50)) for the data being returned

USE lolita;

-- Increase size of recommendation columns to handle longer AI responses
ALTER TABLE screenplay_analyses 
MODIFY COLUMN grok_recommendation TEXT,
MODIFY COLUMN openai_recommendation TEXT;

-- Also ensure other potentially problematic columns are large enough
ALTER TABLE screenplay_analyses 
MODIFY COLUMN grok_verdict LONGTEXT,
MODIFY COLUMN openai_verdict LONGTEXT,
MODIFY COLUMN one_line_verdict LONGTEXT;

-- Show the updated column definitions
DESCRIBE screenplay_analyses;
