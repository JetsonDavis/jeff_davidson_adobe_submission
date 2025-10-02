-- Add brand and product_name columns to briefs table
ALTER TABLE briefs
ADD COLUMN IF NOT EXISTS brand VARCHAR(255),
ADD COLUMN IF NOT EXISTS product_name VARCHAR(255);
