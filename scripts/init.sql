-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE user_role AS ENUM ('Assessor', 'Lender', 'Insurer', 'Broker', 'Admin');
CREATE TYPE assessment_status AS ENUM ('queued', 'processing', 'completed', 'failed');
CREATE TYPE review_priority AS ENUM ('standard', 'high');
CREATE TYPE review_status AS ENUM ('pending', 'approved', 'overridden');

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE vehicleiq TO vehicleiq;
