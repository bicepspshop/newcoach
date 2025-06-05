-- Coach Assistant Database Schema Fix
-- Создание правильной структуры базы данных

-- Удаляем существующие таблицы если они есть (ОСТОРОЖНО!)
DROP TABLE IF EXISTS trainer_client CASCADE;
DROP TABLE IF EXISTS workouts CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS coaches CASCADE;

-- 1. Таблица тренеров
CREATE TABLE coaches (
    id BIGSERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Таблица клиентов с обязательной ссылкой на тренера
CREATE TABLE clients (
    id BIGSERIAL PRIMARY KEY,
    coach_id BIGINT NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    telegram_id VARCHAR(50),
    phone VARCHAR(20),
    notes TEXT,
    fitness_goal VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Таблица тренировок с обязательными ссылками
CREATE TABLE workouts (
    id BIGSERIAL PRIMARY KEY,
    coach_id BIGINT NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    exercises JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    workout_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'planned' 
        CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Таблица связей тренер-клиент (для совместимости)
CREATE TABLE trainer_client (
    id BIGSERIAL PRIMARY KEY,
    trainer_id BIGINT NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trainer_id, client_id)
);

-- 5. Создание индексов для быстрой работы
CREATE INDEX idx_coaches_telegram_id ON coaches(telegram_id);
CREATE INDEX idx_clients_coach_id ON clients(coach_id);
CREATE INDEX idx_clients_telegram_id ON clients(telegram_id);
CREATE INDEX idx_workouts_coach_id ON workouts(coach_id);
CREATE INDEX idx_workouts_client_id ON workouts(client_id);
CREATE INDEX idx_workouts_date ON workouts(date);
CREATE INDEX idx_trainer_client_trainer_id ON trainer_client(trainer_id);
CREATE INDEX idx_trainer_client_client_id ON trainer_client(client_id);

-- 6. Восстанавливаем вашего тренера
INSERT INTO coaches (id, telegram_id, name, username, created_at, updated_at) 
VALUES (1, '234104161', 'aNm0ff', 'aNm0ff', NOW(), NOW());

-- Сбрасываем последовательность для coaches
SELECT setval('coaches_id_seq', 1, true);

-- 7. Включаем Row Level Security (RLS)
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trainer_client ENABLE ROW LEVEL SECURITY;

-- 8. Создаем политики для публичного доступа
CREATE POLICY "Allow all operations for coaches" ON coaches FOR ALL USING (true);
CREATE POLICY "Allow all operations for clients" ON clients FOR ALL USING (true);
CREATE POLICY "Allow all operations for workouts" ON workouts FOR ALL USING (true);
CREATE POLICY "Allow all operations for trainer_client" ON trainer_client FOR ALL USING (true);

-- 9. Добавляем тестовые данные
INSERT INTO clients (coach_id, name, phone, notes, fitness_goal) VALUES
(1, 'Тестовый Клиент 1', '+7 (999) 123-45-67', 'Тестовый клиент для проверки синхронизации', 'weight_loss'),
(1, 'Анна Спортивная', '+7 (999) 876-54-32', 'Цель: набор мышечной массы', 'muscle_gain');

-- Добавляем связи тренер-клиент
INSERT INTO trainer_client (trainer_id, client_id) 
SELECT 1, id FROM clients WHERE coach_id = 1;

-- Добавляем тестовые тренировки
INSERT INTO workouts (coach_id, client_id, date, notes, workout_type, status) 
SELECT 
    1, 
    c.id, 
    NOW() + INTERVAL '1 day', 
    'Тестовая тренировка для ' || c.name, 
    'strength_training',
    'planned'
FROM clients c WHERE c.coach_id = 1;

-- 10. Проверяем результат
SELECT 'Схема базы данных создана успешно!' as status;

SELECT 'Таблица coaches:' as info, COUNT(*) as count FROM coaches
UNION ALL
SELECT 'Таблица clients:' as info, COUNT(*) as count FROM clients  
UNION ALL
SELECT 'Таблица workouts:' as info, COUNT(*) as count FROM workouts
UNION ALL
SELECT 'Таблица trainer_client:' as info, COUNT(*) as count FROM trainer_client;

-- Показываем структуру таблицы clients
SELECT 
    'Структура таблицы clients:' as info,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'clients' 
ORDER BY ordinal_position;
