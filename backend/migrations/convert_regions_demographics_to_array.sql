-- Convert regions and demographics from JSONB to VARCHAR[]

-- First, create temporary columns with the new type
ALTER TABLE briefs ADD COLUMN regions_temp VARCHAR[];
ALTER TABLE briefs ADD COLUMN demographics_temp VARCHAR[];

-- Convert JSONB arrays to PostgreSQL arrays
UPDATE briefs SET regions_temp = ARRAY(SELECT jsonb_array_elements_text(regions));
UPDATE briefs SET demographics_temp = ARRAY(SELECT jsonb_array_elements_text(demographics));

-- Drop old columns and rename new ones
ALTER TABLE briefs DROP COLUMN regions;
ALTER TABLE briefs DROP COLUMN demographics;
ALTER TABLE briefs RENAME COLUMN regions_temp TO regions;
ALTER TABLE briefs RENAME COLUMN demographics_temp TO demographics;

-- Add NOT NULL constraints
ALTER TABLE briefs ALTER COLUMN regions SET NOT NULL;
ALTER TABLE briefs ALTER COLUMN demographics SET NOT NULL;
