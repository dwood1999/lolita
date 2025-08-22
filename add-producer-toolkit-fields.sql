-- Add Producer Toolkit fields to screenplay_analyses table
-- Migration: Add DeepSeek financial analysis and Perplexity market research fields

-- DeepSeek Financial Analysis Fields
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_box_office_prediction JSON;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_budget_optimization JSON;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_roi_analysis JSON;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_risk_assessment JSON;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_production_optimization JSON;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_financial_score DECIMAL(3,1) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_confidence DECIMAL(3,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_recommendation TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_cost DECIMAL(8,4) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_processing_time DECIMAL(8,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_success BOOLEAN DEFAULT FALSE;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_error_message TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN deepseek_raw_response LONGTEXT;

-- Perplexity Market Research Fields
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_market_trends JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_competitive_analysis JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_industry_reports JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_distribution_strategy JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_talent_intelligence JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_financial_intelligence JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_sources_cited JSON;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_market_score DECIMAL(3,1) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_competitive_advantage TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_recommendation TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_cost DECIMAL(8,4) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_processing_time DECIMAL(8,2) DEFAULT 0.0;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_research_date TIMESTAMP;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_data_freshness TEXT;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_success BOOLEAN DEFAULT FALSE;
ALTER TABLE screenplay_analyses ADD COLUMN perplexity_error_message TEXT;

-- Add indexes for better query performance
CREATE INDEX idx_screenplay_analyses_deepseek_score ON screenplay_analyses(deepseek_financial_score);
CREATE INDEX idx_screenplay_analyses_deepseek_success ON screenplay_analyses(deepseek_success);
CREATE INDEX idx_screenplay_analyses_perplexity_score ON screenplay_analyses(perplexity_market_score);
CREATE INDEX idx_screenplay_analyses_perplexity_success ON screenplay_analyses(perplexity_success);
CREATE INDEX idx_screenplay_analyses_perplexity_date ON screenplay_analyses(perplexity_research_date);
