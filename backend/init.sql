-- Initial database setup for Weak-to-Strong platform
-- This runs when PostgreSQL container starts for the first time

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema for application
CREATE SCHEMA IF NOT EXISTS weak_to_strong;

-- Set default search path
ALTER DATABASE weaktostrong SET search_path TO weak_to_strong, public;

-- Create enum types
CREATE TYPE user_tier AS ENUM ('free', 'pro', 'team', 'enterprise');
CREATE TYPE challenge_difficulty AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE model_tier AS ENUM ('local', 'haiku', 'sonnet');
CREATE TYPE progress_status AS ENUM ('not_started', 'in_progress', 'completed');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    tier user_tier DEFAULT 'free',
    tokens_used_today INTEGER DEFAULT 0,
    github_id VARCHAR(50),
    google_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table
CREATE TABLE IF NOT EXISTS tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Challenges table
CREATE TABLE IF NOT EXISTS challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    track_id UUID NOT NULL REFERENCES tracks(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    difficulty challenge_difficulty NOT NULL,
    order_index INTEGER NOT NULL,
    model_tier model_tier NOT NULL,
    requirements JSONB NOT NULL DEFAULT '[]',
    constraints JSONB NOT NULL DEFAULT '[]',
    test_config JSONB NOT NULL DEFAULT '{}',
    hints JSONB NOT NULL DEFAULT '[]',
    is_red_team BOOLEAN DEFAULT false,
    points INTEGER DEFAULT 100,
    estimated_time_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Progress tracking
CREATE TABLE IF NOT EXISTS progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    challenge_id UUID NOT NULL REFERENCES challenges(id),
    status progress_status DEFAULT 'not_started',
    attempts INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    best_score INTEGER DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, challenge_id)
);

-- Submissions
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    challenge_id UUID NOT NULL REFERENCES challenges(id),
    code TEXT NOT NULL,
    test_results JSONB,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    challenge_id UUID REFERENCES challenges(id),
    messages JSONB NOT NULL DEFAULT '[]',
    tokens_used INTEGER DEFAULT 0,
    model_tier model_tier NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_challenges_track_order ON challenges(track_id, order_index);
CREATE INDEX idx_progress_user_challenge ON progress(user_id, challenge_id);
CREATE INDEX idx_submissions_user_challenge ON submissions(user_id, challenge_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);

-- Insert initial tracks
INSERT INTO tracks (id, name, description, order_index) VALUES
('a1b2c3d4-e5f6-7890-abcd-123456789abc', 'Web Development', 'Frontend development challenges using HTML, CSS, JavaScript, and React', 1),
('b2c3d4e5-f607-8901-bcde-23456789abcd', 'Data Analysis', 'Data manipulation and analysis using Python, pandas, and SQL', 2),
('c3d4e5f6-0708-9012-cdef-3456789abcde', 'Cloud Infrastructure', 'AWS services, containerization, and deployment challenges', 3);

COMMENT ON DATABASE weaktostrong IS 'Weak-to-Strong AI training platform database';