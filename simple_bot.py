#!/usr/bin/env python3
"""
Минимальная версия Coach Assistant Bot
Работает без сложных зависимостей, только с HTTP API
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Простые зависимости
import requests
from dotenv import load_dotenv

# Загружаем окружение
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.web_app_url = os.getenv('WEB_APP_URL', 'https://bicepspshop.github.io/newcoach/')
        
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в .env файле")
        
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Database setup (используем существующий код)
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        try:
            from database.connection_fallback import simple_db
            self.db = simple_db
            logger.info("✅ Database connected via HTTP API")
        except ImportError as e:
            logger.error(f"❌ Cannot import database: {e}")
            self.db = None
    
    def make_request(self, method: str, data: Dict = None) -> Optional[Dict]:
        """Отправить запрос к Telegram API"""
        try:
            url = f"{self.base_url}/{method}"
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def send_message(self, chat_id: int, text: str, reply_markup: Dict = None) -> bool:
        """Отправить сообщение"""
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        result = self.make_request('sendMessage', data)
        return result is not None
    
    def create_inline_keyboard(self, buttons: list) -> Dict:
        """Создать inline клавиатуру"""
        return {
            'inline_keyboard': buttons
        }
    
    def create_button(self, text: str, callback_data: str = None, web_app_url: str = None) -> Dict:
        """Создать кнопку"""
        button = {'text': text}
        
        if callback_data:
            button['callback_data'] = callback_data
        elif web_app_url:
            button['web_app'] = {'url': web_app_url}
            
        return button
    
    def handle_start(self, chat_id: int, user_data: Dict) -> bool:
        """Обработать команду /start"""
        user_id = str(user_data.get('id', ''))
        first_name = user_data.get('first_name', 'Пользователь')
        username = user_data.get('username')
        
        # Регистрируем тренера
        if self.db:
            try:
                coach = self.db.get_coach_by_telegram_id(user_id)
                if not coach:
                    name = f"{first_name} {user_data.get('last_name', '')}".strip()
                    coach_id = self.db.create_coach(user_id, name, username)
                    logger.info(f"New coach registered: {name} (ID: {coach_id})")
                    
                    text = f"""
🎉 <b>Добро пожаловать в Coach Assistant!</b>

Привет, {first_name}! Вы успешно зарегистрированы как тренер.

🚀 <b>Возможности:</b>
• 👥 Управление клиентами
• 💪 Планирование тренировок  
• 📊 Статистика и отчеты
• 🌐 Веб-приложение

Используйте кнопки ниже для начала работы!
"""
                else:
                    text = f"""
👋 <b>С возвращением, {coach['name']}!</b>

Выберите действие:
"""
            except Exception as e:
                logger.error(f"Database error: {e}")
                text = f"""
🤖 <b>Coach Assistant</b>

Добро пожаловать! Сейчас идет подключение к базе данных...

Попробуйте через несколько секунд.
"""
        else:
            text = f"""
🤖 <b>Coach Assistant</b>

Привет, {first_name}! 

Бот временно работает в ограниченном режиме.
Используйте веб-приложение для полного функционала.
"""
        
        # Создаем клавиатуру
        keyboard = self.create_inline_keyboard([
            [
                self.create_button("👥 Клиенты", "clients"),
                self.create_button("💪 Тренировки", "workouts")
            ],
            [
                self.create_button("📊 Статистика", "stats"),
                self.create_button("🌐 Веб-приложение", web_app_url=self.web_app_url)
            ],
            [
                self.create_button("❓ Помощь", "help")
            ]
        ])
        
        return self.send_message(chat_id, text, keyboard)
    
    def handle_callback(self, chat_id: int, message_id: int, callback_data: str, user_data: Dict) -> bool:
        """Обработать callback query"""
        if callback_data == "clients":
            text = """
👥 <b>Управление клиентами</b>

Для полного управления клиентами используйте веб-приложение.
Там вы можете:

• Добавлять новых клиентов
• Редактировать информацию
• Просматривать историю тренировок
• Анализировать прогресс

Нажмите кнопку "Веб-приложение" ниже.
"""
        elif callback_data == "workouts":
            text = """
💪 <b>Планирование тренировок</b>

В веб-приложении вы можете:

• Создавать тренировки
• Планировать расписание
• Отслеживать выполнение
• Анализировать результаты

Используйте веб-приложение для удобной работы!
"""
        elif callback_data == "stats":
            text = """
📊 <b>Статистика</b>

Детальная статистика доступна в веб-приложении:

• Количество клиентов
• Выполненные тренировки
• Прогресс по целям
• Графики и отчеты

Откройте веб-приложение для просмотра!
"""
        elif callback_data == "help":
            text = """
❓ <b>Помощь</b>

<b>Coach Assistant</b> - ваш помощник в управлении тренировками.

🔧 <b>Команды:</b>
/start - Главное меню
/help - Эта справка

🌐 <b>Веб-приложение:</b>
Основная работа происходит в веб-приложении, которое предоставляет полный функционал для управления клиентами и тренировками.

💡 <b>Поддержка:</b>
При возникновении проблем обратитесь к разработчику.
"""
        else:
            text = "❓ Неизвестная команда. Используйте кнопки меню."
        
        # Создаем клавиатуру с возвратом в главное меню
        keyboard = self.create_inline_keyboard([
            [self.create_button("🌐 Веб-приложение", web_app_url=self.web_app_url)],
            [self.create_button("🔙 Главное меню", "start")]
        ])
        
        # Редактируем сообщение
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'reply_markup': keyboard,
            'parse_mode': 'HTML'
        }
        
        result = self.make_request('editMessageText', data)
        return result is not None
    
    def get_updates(self, offset: int = 0) -> list:
        """Получить обновления"""
        data = {
            'offset': offset,
            'timeout': 30,
            'allowed_updates': ['message', 'callback_query']
        }
        
        result = self.make_request('getUpdates', data)
        if result and result.get('ok'):
            return result.get('result', [])
        return []
    
    def run(self):
        """Запустить бота"""
        logger.info("🚀 Simple Coach Assistant Bot starting...")
        logger.info(f"🌐 Web App URL: {self.web_app_url}")
        
        # Проверяем подключение
        result = self.make_request('getMe')
        if not result or not result.get('ok'):
            logger.error("❌ Cannot connect to Telegram API")
            return
        
        bot_info = result.get('result', {})
        logger.info(f"✅ Bot connected: @{bot_info.get('username')}")
        
        offset = 0
        
        try:
            while True:
                updates = self.get_updates(offset)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    try:
                        # Обработка сообщений
                        if 'message' in update:
                            message = update['message']
                            chat_id = message['chat']['id']
                            user_data = message['from']
                            text = message.get('text', '')
                            
                            if text.startswith('/start'):
                                self.handle_start(chat_id, user_data)
                            elif text.startswith('/help'):
                                # Отправляем help как обычное сообщение
                                help_text = """
❓ <b>Помощь Coach Assistant</b>

🔧 <b>Команды:</b>
/start - Главное меню
/help - Эта справка

🌐 <b>Основная работа:</b>
Используйте веб-приложение для полного функционала управления клиентами и тренировками.

💡 Нажмите /start для доступа к меню.
"""
                                keyboard = self.create_inline_keyboard([
                                    [self.create_button("🌐 Веб-приложение", web_app_url=self.web_app_url)],
                                    [self.create_button("🏠 Главное меню", "start")]
                                ])
                                self.send_message(chat_id, help_text, keyboard)
                            else:
                                # Неизвестное сообщение
                                self.send_message(chat_id, "❓ Используйте /start для доступа к меню")
                        
                        # Обработка callback queries
                        elif 'callback_query' in update:
                            callback = update['callback_query']
                            chat_id = callback['message']['chat']['id']
                            message_id = callback['message']['message_id']
                            callback_data = callback['data']
                            user_data = callback['from']
                            
                            if callback_data == "start":
                                self.handle_start(chat_id, user_data)
                            else:
                                self.handle_callback(chat_id, message_id, callback_data, user_data)
                            
                            # Подтверждаем callback
                            self.make_request('answerCallbackQuery', {
                                'callback_query_id': callback['id']
                            })
                            
                    except Exception as e:
                        logger.error(f"Error processing update: {e}")
                        continue
                        
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"💥 Bot error: {e}")

def main():
    """Главная функция"""
    try:
        bot = SimpleBot()
        bot.run()
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
