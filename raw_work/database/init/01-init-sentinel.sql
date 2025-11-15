-- PROJECT SENTINEL - POSTGRESQL INITIALIZATION SCRIPT
-- Cameroon Defense Force OSINT Analysis System Database Setup

-- Create the main database (already done by docker-compose)
-- Database: sentinel_defense

-- Create extensions for advanced functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS intelligence;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS security;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA intelligence TO sentinel_admin;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO sentinel_admin;
GRANT ALL PRIVILEGES ON SCHEMA security TO sentinel_admin;
GRANT ALL PRIVILEGES ON SCHEMA monitoring TO sentinel_admin;

-- Create optimized indexes for news articles
-- (Django will create tables, we'll add optimizations)

-- Function for full-text search in French and English
CREATE OR REPLACE FUNCTION public.immutable_unaccent(text)
RETURNS text AS $$
SELECT unaccent($1)
$$ LANGUAGE sql IMMUTABLE;

-- Create custom indexes after Django migration
-- These will be added by our migration script

-- Log successful initialization
INSERT INTO public.django_migrations (app, name, applied) 
VALUES ('sentinel_init', '0001_postgresql_setup', NOW())
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'PROJECT SENTINEL PostgreSQL Database initialized successfully!';
    RAISE NOTICE 'Database: sentinel_defense';
    RAISE NOTICE 'User: sentinel_admin';
    RAISE NOTICE 'Extensions: uuid-ossp, pg_trgm, btree_gin, unaccent';
    RAISE NOTICE 'Schemas: intelligence, analytics, security, monitoring';
END $$;

