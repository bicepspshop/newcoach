"""
Telegram keyboards for Coach Assistant Bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard(web_app_url: str = None) -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text="👥 Клиенты", callback_data="clients"),
        InlineKeyboardButton(text="💪 Тренировки", callback_data="workouts")
    )
    keyboard.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
    )
    
    if web_app_url:
        keyboard.row(
            InlineKeyboardButton(text="🌐 Веб-приложение", web_app=WebAppInfo(url=web_app_url))
        )
    
    return keyboard.as_markup()


def clients_menu_keyboard() -> InlineKeyboardMarkup:
    """Clients menu keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text="➕ Добавить клиента", callback_data="add_client")
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def cancel_keyboard(back_to: str = "main_menu") -> InlineKeyboardMarkup:
    """Cancel/back keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data=back_to)
    )
    return keyboard.as_markup()


def skip_keyboard(skip_action: str, cancel_action: str = "main_menu") -> InlineKeyboardMarkup:
    """Skip and cancel keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=skip_action)
    )
    keyboard.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_action)
    )
    return keyboard.as_markup()
