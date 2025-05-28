/**
 * Telegram WebApp Theme Integration
 * Автоматически адаптирует тему приложения под тему Telegram
 */

class TelegramTheme {
    constructor() {
        this.tg = window.Telegram?.WebApp;
        this.isInitialized = false;
        this.currentTheme = null;
    }

    init() {
        if (this.isInitialized) return;
        
        if (this.tg) {
            // Применяем тему Telegram
            this.applyTelegramTheme();
            
            // Слушаем изменения темы
            this.tg.onEvent('themeChanged', () => {
                this.applyTelegramTheme();
            });
            
            // Настраиваем WebApp
            this.tg.expand();
            this.tg.ready();
            
            // Скрываем кнопку "Назад" если нужно
            this.tg.BackButton.hide();
            
        } else {
            // Fallback для тестирования без Telegram
            this.applyFallbackTheme();
        }
        
        this.isInitialized = true;
    }

    applyTelegramTheme() {
        if (!this.tg?.themeParams) return;
        
        const theme = this.tg.themeParams;
        const root = document.documentElement;
        
        // Определяем, темная ли тема
        const isDark = this.isDarkColor(theme.bg_color);
        
        // Устанавливаем CSS переменные
        root.style.setProperty('--tg-bg-color', theme.bg_color || '#ffffff');
        root.style.setProperty('--tg-text-color', theme.text_color || '#000000');
        root.style.setProperty('--tg-hint-color', theme.hint_color || '#999999');
        root.style.setProperty('--tg-link-color', theme.link_color || '#007AFF');
        root.style.setProperty('--tg-button-color', theme.button_color || '#007AFF');
        root.style.setProperty('--tg-button-text-color', theme.button_text_color || '#ffffff');
        root.style.setProperty('--tg-secondary-bg-color', theme.secondary_bg_color || (isDark ? this.lightenColor(theme.bg_color, 0.1) : '#f5f5f5'));
        root.style.setProperty('--tg-header-bg-color', theme.header_bg_color || theme.bg_color || '#ffffff');
        
        // Применяем классы темы
        document.body.classList.remove('telegram-theme', 'telegram-dark', 'telegram-light');
        document.body.classList.add('telegram-theme');
        
        if (isDark) {
            document.body.classList.add('telegram-dark');
        } else {
            document.body.classList.add('telegram-light');
        }
        
        this.currentTheme = { ...theme, isDark };
        
        // Обновляем цвет статус-бара
        if (this.tg.setHeaderColor) {
            this.tg.setHeaderColor(theme.header_bg_color || theme.bg_color);
        }
        
        console.log('Telegram theme applied:', this.currentTheme);
    }

    applyFallbackTheme() {
        // Применяем стандартную тему для тестирования
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        document.body.classList.add('telegram-theme');
        
        if (prefersDark) {
            document.body.classList.add('telegram-dark');
            this.setDarkTheme();
        } else {
            document.body.classList.add('telegram-light');
            this.setLightTheme();
        }
        
        // Слушаем изменения системной темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.remove('telegram-light');
                document.body.classList.add('telegram-dark');
                this.setDarkTheme();
            } else {
                document.body.classList.remove('telegram-dark');
                document.body.classList.add('telegram-light');
                this.setLightTheme();
            }
        });
    }

    setDarkTheme() {
        const root = document.documentElement;
        root.style.setProperty('--tg-bg-color', '#17212b');
        root.style.setProperty('--tg-text-color', '#ffffff');
        root.style.setProperty('--tg-hint-color', '#708499');
        root.style.setProperty('--tg-link-color', '#6ab7ff');
        root.style.setProperty('--tg-button-color', '#5288c1');
        root.style.setProperty('--tg-button-text-color', '#ffffff');
        root.style.setProperty('--tg-secondary-bg-color', '#232e3c');
        root.style.setProperty('--tg-header-bg-color', '#17212b');
        
        console.log('Applied dark theme fallback');
    }

    setLightTheme() {
        const root = document.documentElement;
        root.style.setProperty('--tg-bg-color', '#ffffff');
        root.style.setProperty('--tg-text-color', '#000000');
        root.style.setProperty('--tg-hint-color', '#999999');
        root.style.setProperty('--tg-link-color', '#007AFF');
        root.style.setProperty('--tg-button-color', '#007AFF');
        root.style.setProperty('--tg-button-text-color', '#ffffff');
        root.style.setProperty('--tg-secondary-bg-color', '#f5f5f5');
        root.style.setProperty('--tg-header-bg-color', '#ffffff');
        
        console.log('Applied light theme fallback');
    }

    isDarkColor(color) {
        if (!color) return false;
        
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        
        // Используем формулу восприятия яркости
        const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        return brightness < 128;
    }

    lightenColor(color, factor) {
        if (!color) return '#f0f0f0';
        
        const hex = color.replace('#', '');
        const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + Math.round(255 * factor));
        const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + Math.round(255 * factor));
        const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + Math.round(255 * factor));
        
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // Методы для взаимодействия с Telegram WebApp
    showAlert(message) {
        if (this.tg?.showAlert) {
            this.tg.showAlert(message);
        } else {
            alert(message);
        }
    }

    showConfirm(message, callback) {
        if (this.tg?.showConfirm) {
            this.tg.showConfirm(message, callback);
        } else {
            const result = confirm(message);
            callback(result);
        }
    }

    hapticFeedback(type = 'light') {
        if (this.tg?.HapticFeedback) {
            switch (type) {
                case 'light':
                    this.tg.HapticFeedback.impactOccurred('light');
                    break;
                case 'medium':
                    this.tg.HapticFeedback.impactOccurred('medium');
                    break;
                case 'heavy':
                    this.tg.HapticFeedback.impactOccurred('heavy');
                    break;
                case 'error':
                    this.tg.HapticFeedback.notificationOccurred('error');
                    break;
                case 'success':
                    this.tg.HapticFeedback.notificationOccurred('success');
                    break;
                case 'warning':
                    this.tg.HapticFeedback.notificationOccurred('warning');
                    break;
            }
        }
    }

    close() {
        if (this.tg?.close) {
            this.tg.close();
        } else {
            window.close();
        }
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    isTelegramApp() {
        return !!this.tg;
    }
}

// Создаем глобальный экземпляр
window.telegramTheme = new TelegramTheme();

// Автоматически инициализируем тему при загрузке
document.addEventListener('DOMContentLoaded', () => {
    window.telegramTheme.init();
});

// Экспортируем для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TelegramTheme;
}
