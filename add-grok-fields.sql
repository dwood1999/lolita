ALTER TABLE screenplay_analyses ADD COLUMN grok_score DECIMAL(3,1);
ALTER TABLE screenplay_analyses ADD COLUMN grok_recommendation VARCHAR(50);
ALTER TABLE screenplay_analyses ADD COLUMN grok_verdict TEXT;
