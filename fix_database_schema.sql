-- Coach Assistant Database Schema
-- This script creates the complete database structure for the Coach Assistant app

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (be careful with this in production!)
DROP TABLE IF EXISTS trainer_client CASCADE;
DROP TABLE IF EXISTS workouts CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS coaches CASCADE;

-- Create coaches table
CREATE TABLE coaches (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create clients table with coach_id reference
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    telegram_id VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    notes TEXT,
    fitness_goal VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create workouts table with coach_id reference
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    exercises JSONB DEFAULT '[]',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'planned',
    workout_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create trainer_client relationship table (for compatibility)
CREATE TABLE trainer_client (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trainer_id, client_id)
);

-- Create indexes for better performance
CREATE INDEX idx_coaches_telegram_id ON coaches(telegram_id);
CREATE INDEX idx_clients_coach_id ON clients(coach_id);
CREATE INDEX idx_clients_telegram_id ON clients(telegram_id);
CREATE INDEX idx_workouts_coach_id ON workouts(coach_id);
CREATE INDEX idx_workouts_client_id ON workouts(client_id);
CREATE INDEX idx_workouts_date ON workouts(date);
CREATE INDEX idx_trainer_client_trainer_id ON trainer_client(trainer_id);
CREATE INDEX idx_trainer_client_client_id ON trainer_client(client_id);

-- Insert your existing coach data
INSERT INTO coaches (id, telegram_id, name, username, created_at, updated_at) 
VALUES (1, '234104161', 'aNm0ff', 'aNm0ff', NOW(), NOW())
ON CONFLICT (telegram_id) DO UPDATE SET
    name = EXCLUDED.name,
    username = EXCLUDED.username,
    updated_at = NOW();

-- Reset sequence for coaches table to start from 2
SELECT setval('coaches_id_seq', GREATEST(1, (SELECT MAX(id) FROM coaches)));

-- Enable Row Level Security (RLS) - optional but recommended
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trainer_client ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations for coaches" ON coaches FOR ALL USING (true);
CREATE POLICY "Allow all operations for clients" ON clients FOR ALL USING (true);
CREATE POLICY "Allow all operations for workouts" ON workouts FOR ALL USING (true);
CREATE POLICY "Allow all operations for trainer_client" ON trainer_client FOR ALL USING (true);

-- Add some sample data for testing
INSERT INTO clients (coach_id, name, phone, notes, fitness_goal) VALUES
(1, 'Тестовый Клиент', '+7 (999) 123-45-67', 'Тестовый клиент для проверки', 'weight_loss'),
(1, 'Анна Примерная', '+7 (999) 876-54-32', 'Цель: набор мышечной массы', 'muscle_gain');

-- Add corresponding trainer_client relationships
INSERT INTO trainer_client (trainer_id, client_id) 
SELECT 1, id FROM clients WHERE coach_id = 1
ON CONFLICT (trainer_id, client_id) DO NOTHING;

-- Add some sample workouts
INSERT INTO workouts (coach_id, client_id, date, notes, workout_type, status) 
SELECT 
    1, 
    c.id, 
    NOW() + INTERVAL '1 day', 
    'Тестовая тренировка', 
    'strength_training',
    'planned'
FROM clients c WHERE c.coach_id = 1;

-- Display the results
SELECT 'Database schema created successfully!' as status;
SELECT 'Coaches:' as table_name, COUNT(*) as count FROM coaches;
SELECT 'Clients:' as table_name, COUNT(*) as count FROM clients;
SELECT 'Workouts:' as table_name, COUNT(*) as count FROM workouts;
SELECT 'Trainer-Client relationships:' as table_name, COUNT(*) as count FROM trainer_client;
