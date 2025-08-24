-- Add public sharing capability to screenplay analyses
-- This allows users to make their analysis results publicly viewable

ALTER TABLE screenplay_analyses 
ADD COLUMN is_public BOOLEAN DEFAULT FALSE,
ADD COLUMN public_share_token VARCHAR(64) UNIQUE DEFAULT NULL,
ADD COLUMN shared_at TIMESTAMP NULL DEFAULT NULL;

-- Create index for efficient public lookups
CREATE INDEX idx_public_share_token ON screenplay_analyses(public_share_token);
CREATE INDEX idx_is_public ON screenplay_analyses(is_public);

-- Update existing analyses to be private by default (already done by DEFAULT FALSE)
-- No data migration needed as all existing analyses will remain private
