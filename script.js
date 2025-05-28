/**
 * ТВОЙТРЕНЕР - Coach Assistant Web App
 * Modern iOS-style interface with full functionality
 */

// Configuration
const CONFIG = {
    supabaseUrl: 'https://hgnryhvtcthzmkxxbblz.supabase.co',
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnbnJ5aHZ0Y3Roem1reHhiYmx6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwNzkzMDYsImV4cCI6MjA2MzY1NTMwNn0.ogubE6dLeKO9ziYyGVZ1UivRYHGZDpEfwExdNci4oCQ',
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
        }
    } else {
        // Demo mode for testing
        currentCoach = {
            telegram_id: 'demo_user_' + Math.random().toString(36).substr(2, 9),
            name: 'Demo User',
            username: 'demo'
        };
        console.log('Running in demo mode');
    }
}

// Database operations
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
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: this.headers,
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Database request error:', error);
            showError('Ошибка подключения к базе данных');
            throw error;
        }
    }

    // Coach operations
    async getCoach(telegramId) {
        const coaches = await this.request(`/coaches?telegram_id=eq.${telegramId}`);
        return coaches[0] || null;
    }

    async createCoach(coach) {
        const coaches = await this.request('/coaches', {
            method: 'POST',
            body: JSON.stringify(coach)
        });
        return coaches[0];
    }

    // Client operations
    async getClients(coachId) {
        return await this.request(`/clients?coach_id=eq.${coachId}&order=created_at.desc`);
    }

    async createClient(client) {
        const clients = await this.request('/clients', {
            method: 'POST',
            body: JSON.stringify(client)
        });
        return clients[0];
    }

    async deleteClient(clientId) {
        return await this.request(`/clients?id=eq.${clientId}`, {
            method: 'DELETE'
        });
    }

    // Workout operations
    async getWorkouts(coachId) {
        return await this.request(`/workouts?coach_id=eq.${coachId}&order=date.desc&limit=50`);
    }

    async createWorkout(workout) {
        const workouts = await this.request('/workouts', {
            method: 'POST',
            body: JSON.stringify(workout)
        });
        return workouts[0];
    }

    async updateWorkout(workoutId, updates) {
        return await this.request(`/workouts?id=eq.${workoutId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
    }

    // Stats
    async getStats(coachId) {
        try {
            const [clientsResult, workoutsResult, completedResult] = await Promise.all([
                this.request(`/clients?coach_id=eq.${coachId}`),
                this.request(`/workouts?coach_id=eq.${coachId}`),
                this.request(`/workouts?coach_id=eq.${coachId}&status=eq.completed`)
            ]);

            return {
                clients_count: clientsResult.length,
                workouts_count: workoutsResult.length,
                completed_workouts: completedResult.length
            };
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
                </div>
                ${workout.status === 'planned' ? `
                    <div class="workout-actions">
                        <button class="btn btn-primary btn-sm" onclick="completeWorkout(${workout.id})">
                            Завершить
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="cancelWorkout(${workout.id})">
                            Отменить
                        </button>
                    </div>
                ` : ''}
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
        
        if (!currentCoach?.telegram_id) {
            showError('Не удалось инициализировать пользовательскую сессию');
            return;
        }

        let coach = await db.getCoach(currentCoach.telegram_id);
        if (!coach) {
            coach = await db.createCoach(currentCoach);
        }
        currentCoach = coach;
        
        await loadData();
        setupEventListeners();
        
        setTimeout(() => {
            document.getElementById('loading-overlay').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
        }, 2000);
        
    } catch (error) {
        console.error('App initialization error:', error);
        showError('Ошибка инициализации системы');
        showLoading(false);
    }
}

async function loadData() {
    try {
        const [clientsData, workoutsData, stats] = await Promise.all([
            db.getClients(currentCoach.id),
            db.getWorkouts(currentCoach.id),
            db.getStats(currentCoach.id)
        ]);

        clients = clientsData || [];
        workouts = workoutsData || [];

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
        showError('Ошибка синхронизации данных');
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

    // Add haptic feedback to buttons and interactive elements
    document.addEventListener('click', (e) => {
        if (e.target.matches('.btn, .action-card, .stat-card, .client-item, .workout-card, .schedule-item')) {
            if (window.telegramTheme) {
                window.telegramTheme.hapticFeedback('light');
            }
        }
        
        // Success feedback for primary actions
        if (e.target.matches('.btn-primary')) {
            if (window.telegramTheme) {
                window.telegramTheme.hapticFeedback('success');
            }
        }
        
        // Warning feedback for delete actions
        if (e.target.matches('.btn-danger, .delete-btn')) {
            if (window.telegramTheme) {
                window.telegramTheme.hapticFeedback('warning');
            }
        }
    });

    document.getElementById('add-client-form').addEventListener('submit', handleAddClient);
    document.getElementById('add-workout-form').addEventListener('submit', handleAddWorkout);

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
        
        const clientData = {
            coach_id: currentCoach.id,
            name: document.getElementById('client-name').value.trim(),
            phone: document.getElementById('client-phone').value.trim() || null,
            notes: document.getElementById('client-notes').value.trim() || null,
            fitness_goal: document.getElementById('client-goal').value.trim() || null
        };

        if (!clientData.name) {
            showError('Введите имя клиента');
            return;
        }

        await db.createClient(clientData);
        await loadData();
        
        closeModal('add-client-modal');
        showToast(`Клиент "${clientData.name}" добавлен`);
        
    } catch (error) {
        console.error('Add client error:', error);
        showError('Ошибка при добавлении клиента');
    } finally {
        showLoading(false);
    }
}

async function handleAddWorkout(e) {
    e.preventDefault();
    
    try {
        showLoading(true);
        
        const clientId = parseInt(document.getElementById('workout-client').value);
        const workoutType = document.getElementById('workout-type').value.trim();
        const date = document.getElementById('workout-date').value;
        const notes = document.getElementById('workout-notes').value.trim();

        if (!clientId) {
            showError('Выберите клиента');
            return;
        }

        if (!workoutType) {
            showError('Выберите тип тренировки');
            return;
        }

        if (!date) {
            showError('Выберите дату и время');
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

        await db.createWorkout(workoutData);
        await loadData();
        
        closeModal('add-workout-modal');
        
        const client = clients.find(c => c.id === clientId);
        showToast(`Тренировка для ${client?.name} создана`);
        
    } catch (error) {
        console.error('Add workout error:', error);
        showError('Ошибка при создании тренировки');
    } finally {
        showLoading(false);
    }
}

async function deleteClient(clientId) {
    const client = clients.find(c => c.id === clientId);
    if (!client) return;
    
    const confirmDelete = () => {
        return new Promise((resolve) => {
            if (window.telegramTheme) {
                window.telegramTheme.showConfirm(
                    `Удалить клиента "${client.name}"?\n\nЭто действие нельзя отменить.`, 
                    resolve
                );
            } else {
                resolve(confirm(`Удалить клиента "${client.name}"?\n\nЭто действие нельзя отменить.`));
            }
        });
    };
    
    if (!(await confirmDelete())) {
        return;
    }
    
    try {
        showLoading(true);
        await db.deleteClient(clientId);
        await loadData();
        showToast(`Клиент "${client.name}" удален`);
    } catch (error) {
        console.error('Delete client error:', error);
        showError('Ошибка при удалении клиента');
    } finally {
        showLoading(false);
    }
}

async function deleteWorkout(workoutId) {
    const confirmDelete = () => {
        return new Promise((resolve) => {
            if (window.telegramTheme) {
                window.telegramTheme.showConfirm('Удалить тренировку?', resolve);
            } else {
                resolve(confirm('Удалить тренировку?'));
            }
        });
    };
    
    if (!(await confirmDelete())) return;
    
    try {
        showLoading(true);
        await db.updateWorkout(workoutId, { status: 'cancelled' });
        await loadData();
        showToast('Тренировка удалена');
    } catch (error) {
        console.error('Delete workout error:', error);
        showError('Ошибка при удалении тренировки');
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
        showError('Ошибка при завершении тренировки');
    } finally {
        showLoading(false);
    }
}

async function cancelWorkout(workoutId) {
    const confirmCancel = () => {
        return new Promise((resolve) => {
            if (window.telegramTheme) {
                window.telegramTheme.showConfirm('Отменить тренировку?', resolve);
            } else {
                resolve(confirm('Отменить тренировку?'));
            }
        });
    };
    
    if (!(await confirmCancel())) return;
    
    try {
        showLoading(true);
        await db.updateWorkout(workoutId, { status: 'cancelled' });
        await loadData();
        showToast('Тренировка отменена');
    } catch (error) {
        console.error('Cancel workout error:', error);
        showError('Ошибка при отмене тренировки');
    } finally {
        showLoading(false);
    }
}

// Global functions for HTML onclick events
function openAddClientModal() {
    document.getElementById('add-client-form').reset();
    showModal('add-client-modal');
}

function openAddWorkoutModal() {
    if (clients.length === 0) {
        showError('Необходимо сначала добавить клиентов');
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

function closeApp() {
    if (window.telegramTheme) {
        window.telegramTheme.close();
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
function showError(message) {
    // Error haptic feedback
    if (window.telegramTheme) {
        window.telegramTheme.hapticFeedback('error');
        window.telegramTheme.showAlert(message);
    } else {
        alert(message);
    }
}

function showToast(message, type = 'success') {
    // Haptic feedback based on toast type
    if (window.telegramTheme) {
        if (type === 'success') {
            window.telegramTheme.hapticFeedback('success');
        } else if (type === 'error') {
            window.telegramTheme.hapticFeedback('error');
        } else {
            window.telegramTheme.hapticFeedback('light');
        }
    }
    
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

// Export functions for global access
window.openAddClientModal = openAddClientModal;
window.openAddWorkoutModal = openAddWorkoutModal;
window.closeModal = closeModal;
window.switchToTab = switchToTab;
window.deleteClient = deleteClient;
window.deleteWorkout = deleteWorkout;
window.completeWorkout = completeWorkout;
window.cancelWorkout = cancelWorkout;
window.closeApp = closeApp;
window.toggleMenu = toggleMenu;
window.switchToClientDetail = switchToClientDetail;