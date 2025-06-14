/**
 * ТВОЙТРЕНЕР - Coach Assistant Web App
 * Fixed version with proper coach ID handling
 */

// Configuration - Updated to new Supabase instance
const CONFIG = {
    supabaseUrl: 'https://nludsxoqhhlfpehhblgg.supabase.co',
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdWRzeG9xaGhsZnBlaGhibGdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyODUyNjEsImV4cCI6MjA2Mzg2MTI2MX0.o6DtsgGgpuNQFIL9Gh2Ba-xScVW20dU_IDg4QAYYXxQ',
    telegramWebApp: window.Telegram?.WebApp
};

// Global state
let currentCoach = null;
let clients = [];
let workouts = [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

// Initialize Telegram WebApp
function initTelegramWebApp() {
    const tg = CONFIG.telegramWebApp;
    if (tg) {
        // Show user info
        if (tg.initDataUnsafe?.user) {
            const user = tg.initDataUnsafe.user;
            currentCoach = {
                telegram_id: user.id.toString(),
                name: `${user.first_name} ${user.last_name || ''}`.trim(),
                username: user.username
            };
            console.log('Telegram user detected:', currentCoach);
        }
    } else {
        // Demo mode for testing - using existing coach from database
        currentCoach = {
            telegram_id: '234104161', // aNmOff from your database
            name: 'aNmOff',
            username: 'aNmOff'
        };
        console.log('Running in demo mode with existing coach');
    }
}

// Simple Database operations
class Database {
    constructor() {
        this.baseUrl = `${CONFIG.supabaseUrl}/rest/v1`;
        this.headers = {
            'apikey': CONFIG.supabaseKey,
            'Authorization': `Bearer ${CONFIG.supabaseKey}`,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        };
    }

    async request(endpoint, options = {}) {
        try {
            console.log(`Making request to: ${this.baseUrl}${endpoint}`, options);
            
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: this.headers,
                ...options
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            console.log(`Response from ${endpoint}:`, data);
            return data;
        } catch (error) {
            console.error('Database request error:', error);
            throw error;
        }
    }

    // Coach operations
    async getCoach(telegramId) {
        console.log('Getting coach by telegram_id:', telegramId);
        const coaches = await this.request(`/coaches?telegram_id=eq.${telegramId}`);
        return coaches[0] || null;
    }

    async createCoach(coach) {
        console.log('Creating coach:', coach);
        const coaches = await this.request('/coaches', {
            method: 'POST',
            body: JSON.stringify({
                ...coach,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
        });
        return coaches[0];
    }

    // Client operations
    async getClients(coachId) {
        console.log('Getting clients for coach ID:', coachId);
        
        // Try direct approach first
        let clients = await this.request(`/clients?coach_id=eq.${coachId}&order=created_at.desc`);
        console.log('Direct clients query result:', clients);
        
        // If no results, try through trainer_client relationship
        if (!clients || clients.length === 0) {
            console.log('No direct clients found, trying trainer_client relationship...');
            const relations = await this.request(`/trainer_client?trainer_id=eq.${coachId}`);
            console.log('Trainer-client relations:', relations);
            
            if (relations && relations.length > 0) {
                const clientIds = relations.map(r => r.client_id).join(',');
                clients = await this.request(`/clients?id=in.(${clientIds})&order=created_at.desc`);
                console.log('Clients from relations:', clients);
            }
        }
        
        return clients || [];
    }

    async createClient(client) {
        console.log('Creating client:', client);
        
        try {
            const clients = await this.request('/clients', {
                method: 'POST',
                body: JSON.stringify({
                    ...client,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                })
            });
            
            const newClient = clients[0];
            console.log('Created client:', newClient);
            
            // Also create relationship in trainer_client if it exists
            if (newClient) {
                try {
                    console.log('Creating trainer_client relationship...');
                    const relationship = await this.request('/trainer_client', {
                        method: 'POST',
                        body: JSON.stringify({
                            trainer_id: client.coach_id,
                            client_id: newClient.id,
                            created_at: new Date().toISOString()
                        })
                    });
                    console.log('Created relationship:', relationship);
                } catch (relationError) {
                    console.log('Failed to create trainer_client relationship:', relationError);
                    // This is not critical, continue anyway
                }
            }
            
            return newClient;
        } catch (error) {
            console.error('Error creating client:', error);
            throw error;
        }
    }

    async deleteClient(clientId) {
        console.log('Deleting client:', clientId);
        
        // Delete from trainer_client relationship first
        try {
            await this.request(`/trainer_client?client_id=eq.${clientId}`, {
                method: 'DELETE'
            });
            console.log('Deleted trainer_client relationships');
        } catch (relationError) {
            console.log('No trainer_client relationships to delete:', relationError);
        }
        
        // Delete client
        const result = await this.request(`/clients?id=eq.${clientId}`, {
            method: 'DELETE'
        });
        console.log('Deleted client:', result);
        return result;
    }

    // Workout operations
    async getWorkouts(coachId) {
        console.log('Getting workouts for coach ID:', coachId);
        
        // Try direct approach first
        let workouts = await this.request(`/workouts?coach_id=eq.${coachId}&order=date.desc&limit=50`);
        console.log('Direct workouts query result:', workouts);
        
        // If no results, try through client relationships
        if (!workouts || workouts.length === 0) {
            console.log('No direct workouts found, trying through client relationships...');
            const clients = await this.getClients(coachId);
            if (clients && clients.length > 0) {
                const clientIds = clients.map(c => c.id).join(',');
                workouts = await this.request(`/workouts?client_id=in.(${clientIds})&order=date.desc&limit=50`);
                console.log('Workouts from client relationships:', workouts);
            }
        }
        
        return workouts || [];
    }

    async createWorkout(workout) {
        console.log('Creating workout:', workout);
        
        const workouts = await this.request('/workouts', {
            method: 'POST',
            body: JSON.stringify({
                ...workout,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
        });
        
        const newWorkout = workouts[0];
        console.log('Created workout:', newWorkout);
        return newWorkout;
    }

    async updateWorkout(workoutId, updates) {
        console.log('Updating workout:', workoutId, updates);
        
        const result = await this.request(`/workouts?id=eq.${workoutId}`, {
            method: 'PATCH',
            body: JSON.stringify({
                ...updates,
                updated_at: new Date().toISOString()
            })
        });
        
        console.log('Updated workout:', result);
        return result;
    }

    // Stats
    async getStats(coachId) {
        try {
            console.log('Getting stats for coach ID:', coachId);
            
            const [clientsResult, workoutsResult] = await Promise.all([
                this.getClients(coachId),
                this.getWorkouts(coachId)
            ]);

            const completedWorkouts = workoutsResult.filter(w => w.status === 'completed');

            const stats = {
                clients_count: clientsResult.length,
                workouts_count: workoutsResult.length,
                completed_workouts: completedWorkouts.length
            };
            
            console.log('Calculated stats:', stats);
            return stats;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return {
                clients_count: 0,
                workouts_count: 0,
                completed_workouts: 0
            };
        }
    }
}

const db = new Database();

// Utility functions
function getGoalDisplayName(goal) {
    const goals = {
        'weight_loss': 'Снижение веса',
        'muscle_gain': 'Набор мышечной массы',
        'strength_building': 'Развитие силы',
        'endurance_training': 'Развитие выносливости',
        'marathon_prep': 'Подготовка к марафону',
        'general_fitness': 'Общая физическая подготовка',
        'body_recomposition': 'Изменение композиции тела',
        'athletic_performance': 'Спортивные результаты',
        'injury_recovery': 'Восстановление после травмы',
        'maintenance': 'Поддержание формы',
        'flexibility_mobility': 'Гибкость и подвижность'
    };
    return goals[goal] || goal;
}

function getWorkoutTypeDisplayName(type) {
    const types = {
        'cardio': 'Кардио',
        'strength_training': 'Силовая тренировка',
        'powerlifting': 'Пауэрлифтинг',
        'bodybuilding': 'Бодибилдинг',
        'leg_day': 'День ног',
        'upper_body': 'Верх тела',
        'push_day': 'День жимовых',
        'pull_day': 'День тяговых',
        'full_body': 'Полное тело',
        'core_abs': 'Пресс и кор',
        'hiit': 'Высокоинтенсивные интервалы',
        'endurance': 'Выносливость',
        'flexibility': 'Гибкость и растяжка',
        'sport_specific': 'Специализированная',
        'recovery': 'Восстановительная'
    };
    return types[type] || type;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getClientInitials(name) {
    return name.split(' ').map(word => word[0]).join('').toUpperCase();
}

// UI Management
function showLoading(show = true) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
}

function switchToTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-item').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

function animateCounter(element, targetValue, duration = 800) {
    const startValue = parseInt(element.textContent) || 0;
    const increment = (targetValue - startValue) / (duration / 16);
    let currentValue = startValue;

    const timer = setInterval(() => {
        currentValue += increment;
        if ((increment > 0 && currentValue >= targetValue) || 
            (increment < 0 && currentValue <= targetValue)) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = Math.round(currentValue);
    }, 16);
}

// Render functions
function renderStats(stats) {
    animateCounter(document.getElementById('clients-count'), stats.clients_count);
    animateCounter(document.getElementById('workouts-count'), stats.workouts_count);
    animateCounter(document.getElementById('completed-workouts'), stats.completed_workouts);
    
    const today = new Date().toDateString();
    const todayWorkouts = workouts.filter(w => 
        new Date(w.date).toDateString() === today && w.status === 'planned'
    ).length;
    animateCounter(document.getElementById('today-workouts'), todayWorkouts);
}

function renderTodaySchedule() {
    const container = document.getElementById('today-schedule');
    const today = new Date().toDateString();
    const todayWorkouts = workouts
        .filter(w => new Date(w.date).toDateString() === today)
        .sort((a, b) => new Date(a.date) - new Date(b.date));

    if (!todayWorkouts.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📅</div>
                <h3>Нет тренировок</h3>
                <p>На сегодня тренировки не запланированы</p>
            </div>
        `;
        return;
    }

    container.innerHTML = todayWorkouts.map(workout => {
        const client = clients.find(c => c.id === workout.client_id);
        const date = new Date(workout.date);
        const statusClass = `status-${workout.status}`;
        const statusText = {
            'planned': 'Ожидается',
            'completed': 'Завершено',
            'cancelled': 'Отменено'
        }[workout.status] || workout.status;

        return `
            <div class="schedule-item">
                <div class="schedule-left">
                    <div class="schedule-time">${date.toLocaleTimeString('ru-RU').slice(0, 5)}</div>
                    <div class="schedule-info">
                        <h3>${escapeHtml(client?.name || 'Неизвестный клиент')}</h3>
                        <p>${workout.workout_type ? getWorkoutTypeDisplayName(workout.workout_type) : 'Тренировка'}</p>
                    </div>
                </div>
                <div class="schedule-right">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    ${workout.status === 'planned' ? `
                        <button class="btn btn-sm btn-primary" onclick="completeWorkout(${workout.id})">
                            ✓
                        </button>
                    ` : ''}
                    <button class="delete-btn" onclick="deleteWorkout(${workout.id})">🗑</button>
                </div>
            </div>
        `;
    }).join('');
}

function renderRecentClients() {
    const container = document.getElementById('recent-clients');
    const recentClients = clients.slice(0, 5);

    if (!recentClients.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">👥</div>
                <h3>Нет клиентов</h3>
                <p>Добавьте первого клиента</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recentClients.map(client => {
        const clientWorkouts = workouts.filter(w => w.client_id === client.id);
        const completedWorkouts = clientWorkouts.filter(w => w.status === 'completed').length;
        const progressPercent = clientWorkouts.length > 0 ? 
            Math.round((completedWorkouts / clientWorkouts.length) * 100) : 0;

        return `
            <div class="client-item" onclick="switchToClientDetail(${client.id})">
                <div class="client-left">
                    <div class="client-avatar">${getClientInitials(client.name)}</div>
                    <div class="client-info">
                        <h3>${escapeHtml(client.name)}</h3>
                        <p>Прогресс: ${progressPercent}% • ${client.fitness_goal ? getGoalDisplayName(client.fitness_goal) : 'Без цели'}</p>
                    </div>
                </div>
                <div class="arrow-right">›</div>
            </div>
        `;
    }).join('');
}

function renderClientsList() {
    const container = document.getElementById('clients-list');
    
    if (!clients.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">👥</div>
                <h3>Клиенты отсутствуют</h3>
                <p>Добавьте первого клиента для начала работы</p>
            </div>
        `;
        return;
    }

    container.innerHTML = clients.map(client => {
        const clientWorkouts = workouts.filter(w => w.client_id === client.id);
        const completedWorkouts = clientWorkouts.filter(w => w.status === 'completed').length;
        const progressPercent = clientWorkouts.length > 0 ? 
            Math.round((completedWorkouts / clientWorkouts.length) * 100) : 0;

        return `
            <div class="client-item">
                <div class="client-left">
                    <div class="client-avatar">${getClientInitials(client.name)}</div>
                    <div class="client-info">
                        <h3>${escapeHtml(client.name)}</h3>
                        <p>Прогресс: ${progressPercent}% • ${client.fitness_goal ? getGoalDisplayName(client.fitness_goal) : 'Без цели'}</p>
                        ${client.phone ? `<p>📞 ${escapeHtml(client.phone)}</p>` : ''}
                        ${client.notes ? `<p>📝 ${escapeHtml(client.notes.slice(0, 50))}${client.notes.length > 50 ? '...' : ''}</p>` : ''}
                    </div>
                </div>
                <div class="client-actions">
                    <button class="btn btn-danger btn-sm" onclick="deleteClient(${client.id})">
                        Удалить
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderWorkoutsList() {
    const container = document.getElementById('workouts-list');
    
    if (!workouts.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">💪</div>
                <h3>Тренировки отсутствуют</h3>
                <p>Создайте первую тренировку</p>
            </div>
        `;
        return;
    }

    container.innerHTML = workouts.map(workout => {
        const client = clients.find(c => c.id === workout.client_id);
        const date = new Date(workout.date);
        const statusClass = `status-${workout.status}`;
        const statusText = {
            'planned': 'Запланирована',
            'completed': 'Завершена',
            'cancelled': 'Отменена'
        }[workout.status] || workout.status;

        const hasExercises = workout.exercises && workout.exercises.length > 0;
        const exercisesCount = hasExercises ? workout.exercises.length : 0;

        return `
            <div class="workout-card">
                <div class="workout-header">
                    <div class="workout-title">${escapeHtml(client?.name || 'Неизвестный клиент')}</div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="workout-info">
                    ${workout.workout_type ? `<div>Тип: ${getWorkoutTypeDisplayName(workout.workout_type)}</div>` : ''}
                    <div>Дата: ${date.toLocaleDateString('ru-RU')} в ${date.toLocaleTimeString('ru-RU').slice(0, 5)}</div>
                    ${workout.notes ? `<div>Заметки: ${escapeHtml(workout.notes)}</div>` : ''}
                    ${hasExercises ? `<div>💪 Упражнений: ${exercisesCount}</div>` : ''}
                </div>
                <div class="workout-actions">
                    <button class="btn btn-primary btn-sm" onclick="openWorkoutProgram(${workout.id})">
                        ${hasExercises ? 'Редактировать программу' : 'Составить программу'}
                    </button>
                    ${workout.status === 'planned' ? `
                        <button class="btn btn-success btn-sm" onclick="completeWorkout(${workout.id})">
                            Завершить
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="cancelWorkout(${workout.id})">
                            Отменить
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function populateClientSelect() {
    const select = document.getElementById('workout-client');
    select.innerHTML = '<option value="">Выберите клиента</option>' + 
        clients.map(client => `<option value="${client.id}">${escapeHtml(client.name)}</option>`).join('');
}

// Application logic
async function initApp() {
    try {
        showLoading(true);
        initTelegramWebApp();
        
        console.log('Initialized coach data:', currentCoach);
        
        if (!currentCoach?.telegram_id) {
            console.warn('No coach data available, using fallback');
            currentCoach = {
                id: 1,
                telegram_id: '234104161',
                name: 'aNmOff',
                username: 'aNmOff'
            };
        }

        // Get or create coach in database
        let coach = await db.getCoach(currentCoach.telegram_id);
        console.log('Found coach in database:', coach);
        
        if (!coach) {
            console.log('Coach not found, creating new coach...');
            try {
                coach = await db.createCoach(currentCoach);
                console.log('Created new coach:', coach);
            } catch (error) {
                console.error('Failed to create coach:', error);
                coach = { ...currentCoach, id: 1 }; // Use fallback with ID
            }
        }
        
        // Ensure coach has an ID
        if (!coach.id) {
            console.warn('Coach missing ID, using fallback');
            coach.id = 1; // Fallback ID for aNmOff
        }
        
        currentCoach = coach;
        console.log('Final coach data:', currentCoach);
        
        await loadData();
        setupEventListeners();
        
        // Hide loading after 1.5 seconds
        setTimeout(() => {
            document.getElementById('loading-overlay').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
        }, 1500);
        
    } catch (error) {
        console.error('App initialization error:', error);
        
        // Show app anyway with empty data after 2 seconds
        setTimeout(() => {
            document.getElementById('loading-overlay').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
            showToast('Работаем в автономном режиме', 'info');
        }, 2000);
    }
}

async function loadData() {
    try {
        if (!currentCoach?.id) {
            console.warn('No coach ID available for loading data');
            return;
        }

        console.log('Loading data for coach ID:', currentCoach.id);

        const [clientsData, workoutsData, stats] = await Promise.all([
            db.getClients(currentCoach.id),
            db.getWorkouts(currentCoach.id),
            db.getStats(currentCoach.id)
        ]);

        clients = clientsData || [];
        workouts = workoutsData || [];

        console.log('Loaded clients:', clients);
        console.log('Loaded workouts:', workouts);
        console.log('Loaded stats:', stats);

        renderStats(stats);
        renderTodaySchedule();
        renderRecentClients();
        renderClientsList();
        renderWorkoutsList();
        populateClientSelect();
        
    } catch (error) {
        console.error('Data loading error:', error);
        clients = [];
        workouts = [];
        renderStats({ clients_count: 0, workouts_count: 0, completed_workouts: 0 });
        renderTodaySchedule();
        renderRecentClients();
        renderClientsList();
        renderWorkoutsList();
        populateClientSelect();
    }
}

function setupEventListeners() {
    document.querySelectorAll('.nav-item').forEach(navItem => {
        navItem.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = navItem.dataset.tab;
            
            // Haptic feedback
            if (window.telegramTheme) {
                window.telegramTheme.hapticFeedback('light');
            }
            
            switchToTab(tabName);
        });
    });

    document.getElementById('add-client-form').addEventListener('submit', handleAddClient);
    document.getElementById('add-workout-form').addEventListener('submit', handleAddWorkout);
    document.getElementById('workout-program-form').addEventListener('submit', handleWorkoutProgramSubmit);
    
    // Add event listeners for workout program form changes
    document.getElementById('program-workout-client').addEventListener('change', updateClientInfo);
    document.getElementById('program-workout-date').addEventListener('change', updateClientInfo);

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

// Event handlers
async function handleAddClient(e) {
    e.preventDefault();
    
    try {
        showLoading(true);
        
        console.log('Adding client for coach:', currentCoach);
        
        if (!currentCoach?.id) {
            showToast('Ошибка: ID тренера не найден', 'error');
            return;
        }
        
        const clientData = {
            coach_id: currentCoach.id,
            name: document.getElementById('client-name').value.trim(),
            phone: document.getElementById('client-phone').value.trim() || null,
            notes: document.getElementById('client-notes').value.trim() || null,
            fitness_goal: document.getElementById('client-goal').value.trim() || null
        };

        console.log('Client data to be created:', clientData);

        if (!clientData.name) {
            showToast('Введите имя клиента', 'error');
            return;
        }

        const newClient = await db.createClient(clientData);
        console.log('Successfully created client:', newClient);
        
        if (!newClient) {
            throw new Error('Failed to create client - no data returned');
        }
        
        await loadData();
        
        closeModal('add-client-modal');
        showToast(`Клиент "${clientData.name}" добавлен`);
        
    } catch (error) {
        console.error('Add client error:', error);
        showToast(`Ошибка при добавлении клиента: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleAddWorkout(e) {
    e.preventDefault();
    
    try {
        showLoading(true);
        
        if (!currentCoach?.id) {
            showToast('Ошибка: ID тренера не найден', 'error');
            return;
        }
        
        const clientId = parseInt(document.getElementById('workout-client').value);
        const workoutType = document.getElementById('workout-type').value.trim();
        const date = document.getElementById('workout-date').value;
        const notes = document.getElementById('workout-notes').value.trim();

        if (!clientId) {
            showToast('Выберите клиента', 'error');
            return;
        }

        if (!workoutType) {
            showToast('Выберите тип тренировки', 'error');
            return;
        }

        if (!date) {
            showToast('Выберите дату и время', 'error');
            return;
        }

        const workoutData = {
            coach_id: currentCoach.id,
            client_id: clientId,
            date: date,
            notes: notes || null,
            exercises: [],
            status: 'planned',
            workout_type: workoutType
        };

        console.log('Workout data to be created:', workoutData);

        const newWorkout = await db.createWorkout(workoutData);
        console.log('Successfully created workout:', newWorkout);
        
        if (!newWorkout) {
            throw new Error('Failed to create workout - no data returned');
        }
        
        await loadData();
        
        closeModal('add-workout-modal');
        
        const client = clients.find(c => c.id === clientId);
        showToast(`Тренировка для ${client?.name} создана`);
        
    } catch (error) {
        console.error('Add workout error:', error);
        showToast(`Ошибка при создании тренировки: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteClient(clientId) {
    const client = clients.find(c => c.id === clientId);
    if (!client) return;
    
    if (!confirm(`Удалить клиента "${client.name}"?\n\nЭто действие нельзя отменить.`)) {
        return;
    }
    
    try {
        showLoading(true);
        await db.deleteClient(clientId);
        await loadData();
        showToast(`Клиент "${client.name}" удален`);
    } catch (error) {
        console.error('Delete client error:', error);
        showToast('Ошибка при удалении клиента', 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteWorkout(workoutId) {
    if (!confirm('Удалить тренировку?')) return;
    
    try {
        showLoading(true);
        await db.updateWorkout(workoutId, { status: 'cancelled' });
        await loadData();
        showToast('Тренировка удалена');
    } catch (error) {
        console.error('Delete workout error:', error);
        showToast('Ошибка при удалении тренировки', 'error');
    } finally {
        showLoading(false);
    }
}

async function completeWorkout(workoutId) {
    try {
        showLoading(true);
        await db.updateWorkout(workoutId, { status: 'completed' });
        await loadData();
        showToast('Тренировка завершена');
    } catch (error) {
        console.error('Complete workout error:', error);
        showToast('Ошибка при завершении тренировки', 'error');
    } finally {
        showLoading(false);
    }
}

async function cancelWorkout(workoutId) {
    if (!confirm('Отменить тренировку?')) return;
    
    try {
        showLoading(true);
        await db.updateWorkout(workoutId, { status: 'cancelled' });
        await loadData();
        showToast('Тренировка отменена');
    } catch (error) {
        console.error('Cancel workout error:', error);
        showToast('Ошибка при отмене тренировки', 'error');
    } finally {
        showLoading(false);
    }
}

// Workout Program functionality
let currentWorkoutForProgram = null;
let exerciseCounter = 0;
let workoutExercises = [];

// Global functions for HTML onclick events
function openAddClientModal() {
    document.getElementById('add-client-form').reset();
    showModal('add-client-modal');
}

function openAddWorkoutModal() {
    if (clients.length === 0) {
        showToast('Необходимо сначала добавить клиентов', 'error');
        return;
    }
    
    document.getElementById('add-workout-form').reset();
    populateClientSelect();
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0);
    document.getElementById('workout-date').value = tomorrow.toISOString().slice(0, 16);
    
    showModal('add-workout-modal');
}

function openWorkoutProgram(workoutId) {
    const workout = workouts.find(w => w.id === workoutId);
    if (!workout) {
        showToast('Тренировка не найдена', 'error');
        return;
    }
    
    currentWorkoutForProgram = workout;
    initWorkoutProgram(workout);
    showModal('workout-program-modal');
}

function initWorkoutProgram(workout) {
    // Populate client select
    const clientSelect = document.getElementById('program-workout-client');
    clientSelect.innerHTML = '<option value="">Выберите клиента</option>' + 
        clients.map(client => `<option value="${client.id}">${escapeHtml(client.name)}</option>`).join('');
    
    // Set current values
    clientSelect.value = workout.client_id;
    document.getElementById('program-workout-date').value = workout.date.slice(0, 16);
    document.getElementById('program-workout-type').value = workout.workout_type || '';
    document.getElementById('program-workout-notes').value = workout.notes || '';
    
    // Update client info display
    updateClientInfo();
    
    // Load existing exercises or start fresh
    workoutExercises = [];
    exerciseCounter = 0;
    
    if (workout.exercises && workout.exercises.length > 0) {
        workout.exercises.forEach(exercise => {
            addExercise(exercise.name, exercise.sets, exercise.notes);
        });
    }
    
    renderExercises();
}

function updateClientInfo() {
    const clientId = parseInt(document.getElementById('program-workout-client').value);
    const client = clients.find(c => c.id === clientId);
    const date = document.getElementById('program-workout-date').value;
    
    const clientInfoDiv = document.getElementById('workout-client-info');
    
    if (client && date) {
        const formattedDate = new Date(date).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        clientInfoDiv.innerHTML = `
            <div class="client-name">${escapeHtml(client.name)}</div>
            <div class="client-details">Цель: ${client.fitness_goal ? getGoalDisplayName(client.fitness_goal) : 'Не указана'} • Дата: ${formattedDate}</div>
        `;
    } else {
        clientInfoDiv.innerHTML = `
            <div class="client-name">Выберите клиента</div>
            <div class="client-details">Цель: Не указана • Дата: Не выбрана</div>
        `;
    }
}

function closeApp() {
    if (CONFIG.telegramWebApp) {
        CONFIG.telegramWebApp.close();
    } else {
        window.close();
    }
}

function toggleMenu() {
    showToast('Меню в разработке');
}

function switchToClientDetail(clientId) {
    switchToTab('clients');
    showToast('Детали клиента в разработке');
}

// Utility functions
function showToast(message, type = 'success') {
    console.log(`Toast: ${message} (${type})`);
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const colors = {
        success: '#34C759',
        error: '#FF3B30',
        info: '#007AFF'
    };
    
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 20px;
        background: ${colors[type] || colors.success};
        color: white;
        border-radius: 20px;
        font-weight: 500;
        font-size: 14px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(-50%) translateY(-20px);
        opacity: 0;
        transition: all 0.3s ease;
        max-width: 300px;
        text-align: center;
    `;
    
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
        toast.style.opacity = '1';
    });
    
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(-20px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function addExerciseTemplate(exerciseName) {
    addExercise(exerciseName);
}

function addCustomExercise() {
    const exerciseName = prompt('Введите название упражнения:');
    if (exerciseName && exerciseName.trim()) {
        addExercise(exerciseName.trim());
    }
}

function addExercise(name, existingSets = null, notes = '') {
    exerciseCounter++;
    const exerciseId = `exercise-${exerciseCounter}`;
    
    const exercise = {
        id: exerciseId,
        name: name,
        notes: notes,
        sets: existingSets || [
            { reps: '', weight: '', rest: '' }
        ]
    };
    
    workoutExercises.push(exercise);
    renderExercises();
}

function removeExercise(exerciseId) {
    workoutExercises = workoutExercises.filter(ex => ex.id !== exerciseId);
    renderExercises();
}

function addSet(exerciseId) {
    const exercise = workoutExercises.find(ex => ex.id === exerciseId);
    if (exercise) {
        exercise.sets.push({ reps: '', weight: '', rest: '' });
        renderExercises();
    }
}

function removeSet(exerciseId, setIndex) {
    const exercise = workoutExercises.find(ex => ex.id === exerciseId);
    if (exercise && exercise.sets.length > 1) {
        exercise.sets.splice(setIndex, 1);
        renderExercises();
    }
}

function updateSetData(exerciseId, setIndex, field, value) {
    const exercise = workoutExercises.find(ex => ex.id === exerciseId);
    if (exercise && exercise.sets[setIndex]) {
        exercise.sets[setIndex][field] = value;
    }
}

function updateExerciseNotes(exerciseId, notes) {
    const exercise = workoutExercises.find(ex => ex.id === exerciseId);
    if (exercise) {
        exercise.notes = notes;
    }
}

function renderExercises() {
    const container = document.getElementById('exercises-container');
    
    if (workoutExercises.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">Добавьте упражнения для программы тренировки</p>';
        return;
    }

    container.innerHTML = workoutExercises.map(exercise => `
        <div class="exercise-item">
            <div class="exercise-header">
                <div class="exercise-name">${escapeHtml(exercise.name)}</div>
                <button type="button" class="remove-exercise" onclick="removeExercise('${exercise.id}')">&times;</button>
            </div>
            
            <div class="sets-container">
                <div class="sets-header">
                    <div>№</div>
                    <div>Повторения</div>
                    <div>Вес (кг)</div>
                    <div>Отдых (мин)</div>
                    <div></div>
                </div>
                
                ${exercise.sets.map((set, index) => `
                    <div class="set-row">
                        <div class="set-number">${index + 1}</div>
                        <input type="number" class="set-input" placeholder="12" 
                               value="${set.reps}" 
                               onchange="updateSetData('${exercise.id}', ${index}, 'reps', this.value)">
                        <input type="number" class="set-input" placeholder="50" step="0.5"
                               value="${set.weight}" 
                               onchange="updateSetData('${exercise.id}', ${index}, 'weight', this.value)">
                        <input type="number" class="set-input" placeholder="2" step="0.5"
                               value="${set.rest || ''}" 
                               onchange="updateSetData('${exercise.id}', ${index}, 'rest', this.value)">
                        <button type="button" class="remove-set" onclick="removeSet('${exercise.id}', ${index})"
                                ${exercise.sets.length <= 1 ? 'style="opacity: 0.3; pointer-events: none;"' : ''}>
                            &times;
                        </button>
                    </div>
                `).join('')}
                
                <button type="button" class="add-set-btn" onclick="addSet('${exercise.id}')">
                    + Добавить подход
                </button>
            </div>

            <div class="exercise-notes">
                <textarea class="notes-input" placeholder="Заметки к упражнению (техника, особенности выполнения...)"
                          onchange="updateExerciseNotes('${exercise.id}', this.value)">${exercise.notes || ''}</textarea>
            </div>
        </div>
    `).join('');
}

async function handleWorkoutProgramSubmit(e) {
    e.preventDefault();
    
    try {
        showLoading(true);
        
        const clientId = parseInt(document.getElementById('program-workout-client').value);
        const date = document.getElementById('program-workout-date').value;
        const workoutType = document.getElementById('program-workout-type').value;
        const notes = document.getElementById('program-workout-notes').value;
        
        if (!clientId || !date || !workoutType) {
            showToast('Заполните все обязательные поля', 'error');
            return;
        }
        
        // Prepare exercises data for database
        const exercisesData = workoutExercises.map(exercise => ({
            name: exercise.name,
            notes: exercise.notes || '',
            sets: exercise.sets.map(set => ({
                reps: parseInt(set.reps) || 0,
                weight: parseFloat(set.weight) || 0,
                rest: parseFloat(set.rest) || 0
            }))
        }));
        
        const updateData = {
            client_id: clientId,
            date: date,
            workout_type: workoutType,
            notes: notes,
            exercises: exercisesData
        };
        
        console.log('Updating workout with program:', updateData);
        
        await db.updateWorkout(currentWorkoutForProgram.id, updateData);
        
        await loadData();
        closeModal('workout-program-modal');
        
        const client = clients.find(c => c.id === clientId);
        showToast(`Программа тренировки для ${client?.name} сохранена`);
        
    } catch (error) {
        console.error('Save workout program error:', error);
        showToast(`Ошибка при сохранении программы: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Export functions for global access
window.openAddClientModal = openAddClientModal;
window.openAddWorkoutModal = openAddWorkoutModal;
window.openWorkoutProgram = openWorkoutProgram;
window.closeModal = closeModal;
window.switchToTab = switchToTab;
window.deleteClient = deleteClient;
window.deleteWorkout = deleteWorkout;
window.completeWorkout = completeWorkout;
window.cancelWorkout = cancelWorkout;
window.closeApp = closeApp;
window.toggleMenu = toggleMenu;
window.switchToClientDetail = switchToClientDetail;
window.addExerciseTemplate = addExerciseTemplate;
window.addCustomExercise = addCustomExercise;
window.removeExercise = removeExercise;
window.addSet = addSet;
window.removeSet = removeSet;
window.updateSetData = updateSetData;
window.updateExerciseNotes = updateExerciseNotes;
window.updateClientInfo = updateClientInfo;
