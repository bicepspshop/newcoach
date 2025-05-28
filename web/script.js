// Client schedule management
let clientScheduleCache = new Map();

async function toggleClientSchedule(clientId) {
    const scheduleContainer = document.getElementById(`schedule-${clientId}`);
    const toggleButton = document.querySelector(`[data-client-id="${clientId}"].schedule-toggle`);
    
    if (!scheduleContainer || !toggleButton) return;
    
    const isExpanded = scheduleContainer.classList.contains('expanded');
    
    if (isExpanded) {
        // Collapse
        scheduleContainer.classList.remove('expanded');
        toggleButton.classList.remove('active');

    } else {
        // Expand
        scheduleContainer.classList.add('expanded');
        toggleButton.classList.add('active');
        
        // Load schedule if not already loaded
        if (!clientScheduleCache.has(clientId)) {
            await loadClientSchedule(clientId);
        }

    }
}

async function loadClientSchedule(clientId) {
    const scheduleContainer = document.getElementById(`schedule-${clientId}`);
    if (!scheduleContainer) return;
    
    // Show loading
    scheduleContainer.innerHTML = `
        <div class="schedule-loading">
            <div class="mini-spinner"></div>
            Загрузка расписания...
        </div>
    `;
    
    try {
        // Get client workouts
        const clientWorkouts = workouts.filter(w => w.client_id === clientId)
            .filter(w => new Date(w.date) > new Date()) // Only future workouts
            .sort((a, b) => new Date(a.date) - new Date(b.date))
            .slice(0, 10); // Limit to 10 upcoming workouts
        
        // Cache the result
        clientScheduleCache.set(clientId, clientWorkouts);
        
        // Render schedule
        renderClientSchedule(clientId, clientWorkouts);
        
    } catch (error) {
        console.error('Error loading client schedule:', error);
        scheduleContainer.innerHTML = `
            <div class="schedule-empty">
                <div class="schedule-empty-icon">❌</div>
                Ошибка загрузки расписания
            </div>
        `;
    }
}

function renderClientSchedule(clientId, clientWorkouts) {
    const scheduleContainer = document.getElementById(`schedule-${clientId}`);
    if (!scheduleContainer) return;
    
    if (!clientWorkouts || clientWorkouts.length === 0) {
        scheduleContainer.innerHTML = `
            <div class="schedule-empty">
                <div class="schedule-empty-icon">📅</div>
                Нет запланированных тренировок
            </div>
        `;
        return;
    }
    
    const scheduleHTML = `
        <div class="schedule-header">
            <div class="schedule-title">Ближайшие тренировки</div>
            <div class="schedule-count">${clientWorkouts.length}</div>
        </div>
        <div class="schedule-list">
            ${clientWorkouts.map((workout, index) => {
                const date = new Date(workout.date);
                const isToday = date.toDateString() === new Date().toDateString();
                const isTomorrow = date.toDateString() === new Date(Date.now() + 86400000).toDateString();
                
                let dateText = date.toLocaleDateString('ru-RU');
                if (isToday) dateText = 'Сегодня';
                else if (isTomorrow) dateText = 'Завтра';
                
                return `
                    <div class="mini-workout-card">
                        <div class="workout-status-indicator ${workout.status}"></div>
                        <div class="mini-workout-header">
                            <div class="mini-workout-type">
                                ${workout.workout_type ? getWorkoutTypeDisplayName(workout.workout_type) : 'Тренировка'}
                            </div>
                            <div class="mini-workout-date">${dateText}</div>
                        </div>
                        <div class="mini-workout-time">
                            Время: ${date.toLocaleTimeString('ru-RU').slice(0, 5)}
                        </div>
                        ${workout.notes ? `
                            <div class="mini-workout-notes">
                                ${UI.escapeHtml(workout.notes.slice(0, 80))}${workout.notes.length > 80 ? '...' : ''}
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    scheduleContainer.innerHTML = scheduleHTML;
}

// Refresh client schedule when workouts change
function refreshClientSchedules() {
    clientScheduleCache.clear();
    // Reload any expanded schedules
    document.querySelectorAll('.workout-schedule.expanded').forEach(schedule => {
        const clientId = parseInt(schedule.id.replace('schedule-', ''));
        if (clientId) {
            loadClientSchedule(clientId);
        }
    });
}/**
 * Coach Assistant Web App - Modern Edition
 * Enhanced with smooth animations and elegant interactions
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

// Initialize Telegram WebApp with enhanced theming
function initTelegramWebApp() {
    const tg = CONFIG.telegramWebApp;
    if (tg) {
        tg.ready();
        tg.expand();
        
        // Professional theme integration
        applyTelegramTheme(tg.themeParams);
        
        // Listen for theme changes
        tg.onEvent('themeChanged', () => {
            applyTelegramTheme(tg.themeParams);
        });
        
        // Show user info with professional styling
        if (tg.initDataUnsafe?.user) {
            const user = tg.initDataUnsafe.user;
            const userName = document.getElementById('user-name');
            userName.style.opacity = '0';
            userName.textContent = user.first_name;
            
            // Professional fade in
            setTimeout(() => {
                userName.style.transition = 'opacity 0.3s ease';
                userName.style.opacity = '1';
            }, 100);
            
            currentCoach = {
                telegram_id: user.id.toString(),
                name: `${user.first_name} ${user.last_name || ''}`.trim(),
                username: user.username
            };
        }
    } else {
        // Default to system theme if not in Telegram
        const systemTheme = detectSystemTheme();
        document.documentElement.setAttribute('data-theme', systemTheme);
        setupSystemThemeListener();
        console.log(`🎨 Applied ${systemTheme} theme based on system preference`);
        
        // For testing outside Telegram - create a demo user
        const userName = document.getElementById('user-name');
        userName.textContent = 'Demo User';
        
        currentCoach = {
            telegram_id: 'demo_user_' + Math.random().toString(36).substr(2, 9),
            name: 'Demo User',
            username: 'demo'
        };
        
        console.log('Running in demo mode with user:', currentCoach);
    }
}

// Apply Telegram theme to the app
function applyTelegramTheme(themeParams) {
    const root = document.documentElement;
    
    // Detect if using dark theme
    const isDark = themeParams.bg_color && 
                   (themeParams.bg_color.toLowerCase().includes('#1') || 
                    themeParams.bg_color.toLowerCase().includes('#2') ||
                    themeParams.bg_color.toLowerCase().includes('#0'));
    
    const theme = isDark ? 'dark' : 'light';
    root.setAttribute('data-theme', theme);
    
    console.log(`🎨 Applied ${theme} theme based on Telegram settings`);
    
    
}

// Detect system theme for non-Telegram users
function detectSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Listen for system theme changes
function setupSystemThemeListener() {
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener((e) => {
            if (!CONFIG.telegramWebApp) {
                document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
                console.log(`🎨 System theme changed to: ${e.matches ? 'dark' : 'light'}`);
            }
        });
    }
}

// Enhanced Database operations with better error handling
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

    async updateClient(clientId, updates) {
        return await this.request(`/clients?id=eq.${clientId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates)
        });
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

    // Stats with proper counting
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

// Utility functions for translating field values
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

function getWorkoutTypeIcon(type) {
    const icons = {
        'cardio': '🏃‍♂️',
        'strength_training': '🏋️‍♂️',
        'powerlifting': '💪',
        'bodybuilding': '🏆',
        'leg_day': '🦵',
        'upper_body': '💪',
        'push_day': '👊',
        'pull_day': '🤲',
        'full_body': '🔥',
        'core_abs': '🎯',
        'hiit': '⚡',
        'endurance': '🏃‍♀️',
        'flexibility': '🧘‍♀️',
        'sport_specific': '⚽',
        'recovery': '💆‍♀️'
    };
    return icons[type] || '💪';
}

// Enhanced UI Management with animations
class UI {
    static showLoading(show = true) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }

    static showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('active');
        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    static hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('active');
    }

    static switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Update nav tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    static animateCounter(element, targetValue, duration = 800) {
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

    static renderStats(stats) {
        // Professional counter animation
        this.animateCounter(document.getElementById('clients-count'), stats.clients_count);
        this.animateCounter(document.getElementById('workouts-count'), stats.workouts_count);
        this.animateCounter(document.getElementById('completed-workouts'), stats.completed_workouts);
    }

    static renderClients(clientsList) {
        const container = document.getElementById('clients-list');
        
        if (!clientsList.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">👥</div>
                    <h3>Клиенты отсутствуют</h3>
                    <p>Добавьте первого клиента для начала работы с системой управления тренировками</p>
                </div>
            `;
            return;
        }

        container.innerHTML = clientsList.map((client, index) => `
            <div class="client-card" data-client-id="${client.id}">
                <div class="client-header">
                    <div class="client-name">${this.escapeHtml(client.name)}</div>
                    <div class="client-actions">
                        <button class="schedule-toggle" onclick="toggleClientSchedule(${client.id})" data-client-id="${client.id}">
                            Расписание
                            <span class="arrow">▼</span>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteClient(${client.id})" title="Удалить клиента">
                            Удалить
                        </button>
                    </div>
                </div>
                <div class="client-info">
                    ${client.fitness_goal ? `<div>Цель: ${getGoalDisplayName(client.fitness_goal)}</div>` : ''}
                    ${client.phone ? `<div>Телефон: ${this.escapeHtml(client.phone)}</div>` : ''}
                    ${client.notes ? `<div>Заметки: ${this.escapeHtml(client.notes)}</div>` : ''}
                    <div><small>Добавлен: ${new Date(client.created_at).toLocaleDateString('ru-RU')}</small></div>
                </div>
                <div class="workout-schedule" id="schedule-${client.id}">
                    <!-- Workout schedule will be loaded here -->
                </div>
            </div>
        `).join('');
    }

    static renderWorkouts(workoutsList) {
        const container = document.getElementById('workouts-list');
        
        if (!workoutsList.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">💪</div>
                    <h3>Тренировки отсутствуют</h3>
                    <p>Создайте первую тренировку для организации профессионального процесса обучения</p>
                </div>
            `;
            return;
        }

        container.innerHTML = workoutsList.map((workout, index) => {
            const client = clients.find(c => c.id === workout.client_id);
            const date = new Date(workout.date);
            const statusClass = `status-${workout.status}`;
            const statusText = {
                'planned': 'Запланирована',
                'completed': 'Завершена',
                'cancelled': 'Отменена'
            }[workout.status] || workout.status;

            return `
                <div class="workout-card" data-workout-id="${workout.id}">
                    <div class="workout-header">
                        <div class="workout-title">${this.escapeHtml(client?.name || 'Неизвестный клиент')}</div>
                        <span class="workout-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="workout-info">
                        ${workout.workout_type ? `<div>Тип: ${getWorkoutTypeDisplayName(workout.workout_type)}</div>` : ''}
                        <div>Дата: ${date.toLocaleDateString('ru-RU')} в ${date.toLocaleTimeString('ru-RU').slice(0, 5)}</div>
                        ${workout.notes ? `<div>Заметки: ${this.escapeHtml(workout.notes)}</div>` : ''}
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

    static renderRecentWorkouts(workoutsList) {
        const container = document.getElementById('recent-workouts');
        const upcoming = workoutsList
            .filter(w => new Date(w.date) > new Date() && w.status === 'planned')
            .slice(0, 5);

        if (!upcoming.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📅</div>
                    <h3>Расписание пусто</h3>
                    <p>Запланируйте тренировки для эффективного управления процессом обучения</p>
                </div>
            `;
            return;
        }

        container.innerHTML = upcoming.map((workout, index) => {
            const client = clients.find(c => c.id === workout.client_id);
            const date = new Date(workout.date);
            const isToday = date.toDateString() === new Date().toDateString();
            const isTomorrow = date.toDateString() === new Date(Date.now() + 86400000).toDateString();
            
            let dateText = date.toLocaleDateString('ru-RU');
            if (isToday) dateText = 'Сегодня';
            else if (isTomorrow) dateText = 'Завтра';
            
            return `
                <div class="workout-card">
                    <div class="workout-header">
                        <div class="workout-title">${this.escapeHtml(client?.name || 'Неизвестный клиент')}</div>
                        <span class="workout-status status-planned">${dateText}</span>
                    </div>
                    <div class="workout-info">
                        ${workout.workout_type ? `<div>Тип: ${getWorkoutTypeDisplayName(workout.workout_type)}</div>` : ''}
                        <div>Время: ${date.toLocaleTimeString('ru-RU').slice(0, 5)}</div>
                        ${workout.notes ? `<div>Заметки: ${this.escapeHtml(workout.notes.slice(0, 60))}${workout.notes.length > 60 ? '...' : ''}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    static populateClientSelect() {
        const select = document.getElementById('workout-client');
        select.innerHTML = '<option value="">Выберите клиента</option>' + 
            clients.map(client => `<option value="${client.id}">${this.escapeHtml(client.name)}</option>`).join('');
    }

    static escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        const colors = {
            success: 'var(--accent-success)',
            error: 'var(--accent-danger)',
            info: 'var(--accent-primary)'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            background: ${colors[type] || colors.success};
            color: white;
            border-radius: var(--radius-md);
            font-weight: 500;
            font-size: 0.875rem;
            z-index: 9999;
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
        });
        
        // Animate out and remove
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Application logic with enhanced error handling
async function initApp() {
    try {
        UI.showLoading(true);
        
        initTelegramWebApp();
        
        if (!currentCoach?.telegram_id) {
            showError('Не удалось инициализировать пользовательскую сессию');
            return;
        }

        console.log('Initializing app for user:', currentCoach);

        // Get or create coach
        let coach = await db.getCoach(currentCoach.telegram_id);
        console.log('Found existing coach:', coach);
        
        if (!coach) {
            console.log('Creating new coach...');
            coach = await db.createCoach(currentCoach);
            console.log('Created coach:', coach);
            UI.showToast('Аккаунт тренера успешно создан', 'success');
        }
        currentCoach = coach;
        
        console.log('Final coach object:', currentCoach);

        // Load data with progress
        await loadData();
        
        // Setup event listeners
        setupEventListeners();
        
        UI.showLoading(false);
        UI.showToast('Система успешно инициализирована', 'success');
        
    } catch (error) {
        console.error('App initialization error:', error);
        showError('Ошибка инициализации системы');
        UI.showLoading(false);
    }
}

async function loadData() {
    try {
        console.log('Loading data for coach:', currentCoach.id);
        
        const [clientsData, workoutsData, stats] = await Promise.all([
            db.getClients(currentCoach.id),
            db.getWorkouts(currentCoach.id),
            db.getStats(currentCoach.id)
        ]);

        clients = clientsData || [];
        workouts = workoutsData || [];
        
        console.log('Loaded data:', {
            clients: clients.length,
            workouts: workouts.length,
            stats: stats
        });

        UI.renderStats(stats);
        UI.renderClients(clients);
        UI.renderWorkouts(workouts);
        UI.renderRecentWorkouts(workouts);
        UI.populateClientSelect();
        
        // Refresh client schedules
        refreshClientSchedules();

    } catch (error) {
        console.error('Data loading error:', error);
        
        // Set empty data on error
        clients = [];
        workouts = [];
        
        // Render empty state
        UI.renderStats({ clients_count: 0, workouts_count: 0, completed_workouts: 0 });
        UI.renderClients([]);
        UI.renderWorkouts([]);
        UI.renderRecentWorkouts([]);
        UI.populateClientSelect();
        
        showError('Ошибка синхронизации данных');
    }
}

function setupEventListeners() {
    // Enhanced tab navigation
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = tab.dataset.tab;
            UI.switchTab(tabName);
            
            // Haptic feedback for Telegram WebApp
            if (CONFIG.telegramWebApp?.HapticFeedback) {
                CONFIG.telegramWebApp.HapticFeedback.impactOccurred('light');
            }
        });
    });

    // Modal controls with animations
    document.querySelectorAll('[data-modal]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = btn.dataset.modal;
            UI.hideModal(modalId);
        });
    });

    // Add client button
    document.getElementById('add-client-btn').addEventListener('click', () => {
        document.getElementById('add-client-form').reset();
        UI.showModal('add-client-modal');
    });

    // Add workout button
    document.getElementById('add-workout-btn').addEventListener('click', () => {
        if (clients.length === 0) {
            showError('Необходимо сначала добавить клиентов');
            return;
        }
        
        document.getElementById('add-workout-form').reset();
        UI.populateClientSelect();
        
        // Set default date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(10, 0);
        document.getElementById('workout-date').value = tomorrow.toISOString().slice(0, 16);
        
        UI.showModal('add-workout-modal');
    });

    // Form submissions
    document.getElementById('add-client-form').addEventListener('submit', handleAddClient);
    document.getElementById('add-workout-form').addEventListener('submit', handleAddWorkout);

    // Close modals on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                const modalId = modal.id;
                UI.hideModal(modalId);
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(modal => {
                UI.hideModal(modal.id);
            });
        }
    });
}

async function handleAddClient(e) {
    e.preventDefault();
    
    try {
        UI.showLoading(true);
        
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
        
        UI.hideModal('add-client-modal');
        UI.showToast(`Клиент "${clientData.name}" добавлен`, 'success');

        
    } catch (error) {
        console.error('Add client error:', error);
        showError('Ошибка при добавлении клиента');
    } finally {
        UI.showLoading(false);
    }
}

async function handleAddWorkout(e) {
    e.preventDefault();
    
    try {
        UI.showLoading(true);
        
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
        
        UI.hideModal('add-workout-modal');
        
        const client = clients.find(c => c.id === clientId);
        UI.showToast(`Тренировка для ${client?.name} создана`, 'success');
        
    } catch (error) {
        console.error('Add workout error:', error);
        showError('Ошибка при создании тренировки');
    } finally {
        UI.showLoading(false);
    }
}

async function deleteClient(clientId) {
    const client = clients.find(c => c.id === clientId);
    if (!client) return;
    
    if (!confirm(`Удалить клиента "${client.name}"?\n\nЭто действие нельзя отменить. Все тренировки этого клиента также будут удалены.`)) {
        return;
    }
    
    try {
        UI.showLoading(true);
        await db.deleteClient(clientId);
        await loadData();
        UI.showToast(`Клиент "${client.name}" удален`, 'success');

    } catch (error) {
        console.error('Delete client error:', error);
        showError('Ошибка при удалении клиента');
    } finally {
        UI.showLoading(false);
    }
}

async function completeWorkout(workoutId) {
    try {
        UI.showLoading(true);
        await db.updateWorkout(workoutId, { status: 'completed' });
        await loadData();
        UI.showToast('Тренировка завершена', 'success');
    } catch (error) {
        console.error('Complete workout error:', error);
        showError('Ошибка при завершении тренировки');
    } finally {
        UI.showLoading(false);
    }
}

async function cancelWorkout(workoutId) {
    if (!confirm('Отменить тренировку?')) return;
    
    try {
        UI.showLoading(true);
        await db.updateWorkout(workoutId, { status: 'cancelled' });
        await loadData();
        UI.showToast('Тренировка отменена', 'success');
    } catch (error) {
        console.error('Cancel workout error:', error);
        showError('Ошибка при отмене тренировки');
    } finally {
        UI.showLoading(false);
    }
}

// Enhanced utility functions
function showError(message) {
    if (CONFIG.telegramWebApp) {
        CONFIG.telegramWebApp.showAlert(message);
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    UI.showToast(message, 'success');
}



// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

// Export functions for global access
window.deleteClient = deleteClient;
window.completeWorkout = completeWorkout;
window.cancelWorkout = cancelWorkout;
window.toggleClientSchedule = toggleClientSchedule;
