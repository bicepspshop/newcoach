-- SQL скрипт для создания таблиц в Supabase
-- Выполните этот код в SQL Editor вашего Supabase проекта

-- Создание таблицы тренеров
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы клиентов
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    telegram_id VARCHAR(20),
    phone VARCHAR(20),
    notes TEXT,
    fitness_goal TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы тренировок
CREATE TABLE IF NOT EXISTS workouts (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    exercises JSONB DEFAULT '[]',
    notes TEXT,
    workout_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'planned',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_coaches_telegram_id ON coaches(telegram_id);
CREATE INDEX IF NOT EXISTS idx_clients_coach_id ON clients(coach_id);
CREATE INDEX IF NOT EXISTS idx_workouts_coach_id ON workouts(coach_id);
CREATE INDEX IF NOT EXISTS idx_workouts_client_id ON workouts(client_id);
CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);

-- Включение Row Level Security (RLS)
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;

-- Политики безопасности для coaches
CREATE POLICY "Coaches can view own data" ON coaches
    FOR ALL USING (auth.uid()::text = telegram_id);

-- Политики безопасности для clients
CREATE POLICY "Coaches can manage own clients" ON clients
    FOR ALL USING (
        coach_id IN (
            SELECT id FROM coaches WHERE telegram_id = auth.uid()::text
        )
    );

-- Политики безопасности для workouts
CREATE POLICY "Coaches can manage own workouts" ON workouts
    FOR ALL USING (
        coach_id IN (
            SELECT id FROM coaches WHERE telegram_id = auth.uid()::text
        )
    );

-- Публичная политика для чтения (для анонимного доступа)
CREATE POLICY "Allow anonymous read access" ON coaches
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous read access" ON clients
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous read access" ON workouts
    FOR SELECT USING (true);

-- Разрешения для анонимного пользователя
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;
