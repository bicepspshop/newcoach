"""
Telegram Bot Handlers for Coach Assistant App
Simplified, compact implementation with core functionality
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db

logger = logging.getLogger(__name__)

# States for FSM
class ClientStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_notes = State()

class WorkoutStates(StatesGroup):
    waiting_client = State()
    waiting_date = State()
    waiting_exercises = State()

# Main router
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - register coach and show main menu"""
    await state.clear()
    
    user_id = str(message.from_user.id)
    
    # Get or create coach
    coach = await db.get_coach_by_telegram_id(user_id)
    if not coach:
        name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        coach_id = await db.create_coach(
            telegram_id=user_id,
            name=name,
            username=message.from_user.username
        )
        logger.info(f"New coach registered: {name} (ID: {coach_id})")
        
        welcome_text = f"""
🎉 Добро пожаловать в Coach Assistant!

Привет, {message.from_user.first_name}! Вы успешно зарегистрированы как тренер.

🚀 Что умеет бот:
• 👥 Управление клиентами
• 💪 Планирование тренировок
• 📊 Статистика и отчеты
• 🌐 Веб-приложение

Начните с добавления первого клиента!
"""
    else:
        welcome_text = f"""
👋 С возвращением, {coach['name']}!

Выберите действие:
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="👥 Клиенты", callback_data="clients"),
        InlineKeyboardButton(text="💪 Тренировки", callback_data="workouts")
    )
    keyboard.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        InlineKeyboardButton(text="🌐 Веб-приложение", web_app=WebAppInfo(url=os.getenv('WEB_APP_URL', 'https://your-webapp-url.com')))
    )
    
    await message.answer(welcome_text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    await callback.answer()
    await cmd_start(callback.message, state)

# Client management
@router.callback_query(F.data == "clients")
async def callback_clients(callback: CallbackQuery):
    """Show clients menu"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    coach = await db.get_coach_by_telegram_id(user_id)
    
    if not coach:
        await callback.message.answer("❌ Ошибка: тренер не найден")
        return
    
    clients = await db.get_clients_for_coach(coach['id'])
    
    text = f"👥 Ваши клиенты ({len(clients)}):\n\n"
    
    keyboard = InlineKeyboardBuilder()
    
    if clients:
        for client in clients[:10]:  # Show max 10 clients
            text += f"• {client['name']}"
            if client['phone']:
                text += f" ({client['phone']})"
            text += "\n"
            
            keyboard.row(
                InlineKeyboardButton(
                    text=f"👤 {client['name']}", 
                    callback_data=f"client_{client['id']}"
                )
            )
    else:
        text += "Пока нет клиентов. Добавьте первого!"
    
    keyboard.row(
        InlineKeyboardButton(text="➕ Добавить клиента", callback_data="add_client")
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data == "add_client")
async def callback_add_client(callback: CallbackQuery, state: FSMContext):
    """Start adding new client"""
    await callback.answer()
    await state.set_state(ClientStates.waiting_name)
    
    text = "👤 Добавление нового клиента\n\nВведите имя клиента:"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="clients"))
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@router.message(ClientStates.waiting_name)
async def client_name_received(message: Message, state: FSMContext):
    """Receive client name"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте снова:")
        return
    
    await state.update_data(name=name)
    await state.set_state(ClientStates.waiting_phone)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_phone"))
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="clients"))
    
    await message.answer(
        f"📱 Введите номер телефона для {name} или пропустите:",
        reply_markup=keyboard.as_markup()
    )

@router.message(ClientStates.waiting_phone)
async def client_phone_received(message: Message, state: FSMContext):
    """Receive client phone"""
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await ask_for_notes(message, state)

@router.callback_query(F.data == "skip_phone", ClientStates.waiting_phone)
async def skip_phone(callback: CallbackQuery, state: FSMContext):
    """Skip phone input"""
    await callback.answer()
    await state.update_data(phone=None)
    await ask_for_notes(callback.message, state)

async def ask_for_notes(message: Message, state: FSMContext):
    """Ask for client notes"""
    await state.set_state(ClientStates.waiting_notes)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_notes"))
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="clients"))
    
    await message.answer(
        "📝 Добавьте заметки о клиенте (цели, особенности) или пропустите:",
        reply_markup=keyboard.as_markup()
    )

@router.message(ClientStates.waiting_notes)
async def client_notes_received(message: Message, state: FSMContext):
    """Receive client notes and create client"""
    notes = message.text.strip()
    await state.update_data(notes=notes)
    await create_client_final(message, state)

@router.callback_query(F.data == "skip_notes", ClientStates.waiting_notes)
async def skip_notes(callback: CallbackQuery, state: FSMContext):
    """Skip notes input"""
    await callback.answer()
    await state.update_data(notes=None)
    await create_client_final(callback.message, state)

async def create_client_final(message: Message, state: FSMContext):
    """Create the client with collected data"""
    data = await state.get_data()
    await state.clear()
    
    user_id = str(message.from_user.id)
    coach = await db.get_coach_by_telegram_id(user_id)
    
    try:
        client_id = await db.create_client(
            coach_id=coach['id'],
            name=data['name'],
            phone=data.get('phone'),
            notes=data.get('notes')
        )
        
        text = f"✅ Клиент добавлен!\n\n👤 {data['name']}"
        if data.get('phone'):
            text += f"\n📱 {data['phone']}"
        if data.get('notes'):
            text += f"\n📝 {data['notes']}"
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="👥 К списку клиентов", callback_data="clients"),
            InlineKeyboardButton(text="➕ Добавить еще", callback_data="add_client")
        )
        keyboard.row(
            InlineKeyboardButton(text="💪 Создать тренировку", callback_data=f"create_workout_{client_id}")
        )
        
        await message.answer(text, reply_markup=keyboard.as_markup())
        
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        await message.answer("❌ Ошибка при добавлении клиента. Попробуйте снова.")

# Workout management
@router.callback_query(F.data == "workouts")
async def callback_workouts(callback: CallbackQuery):
    """Show workouts menu"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    coach = await db.get_coach_by_telegram_id(user_id)
    
    if not coach:
        await callback.message.answer("❌ Ошибка: тренер не найден")
        return
    
    workouts = await db.get_workouts_for_coach(coach['id'], limit=10)
    stats = await db.get_stats_for_coach(coach['id'])
    
    text = f"💪 Тренировки\n\n"
    text += f"📊 Всего: {stats['workouts_count']} | Завершено: {stats['completed_workouts']}\n\n"
    
    if workouts:
        text += "📅 Последние тренировки:\n"
        for workout in workouts:
            status_icon = "✅" if workout['status'] == 'completed' else "📅" if workout['status'] == 'planned' else "❌"
            text += f"{status_icon} {workout['date'].strftime('%d.%m %H:%M')} - {workout['client_name']}\n"
    else:
        text += "Пока нет тренировок. Создайте первую!"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="➕ Создать тренировку", callback_data="create_workout")
    )
    if workouts:
        keyboard.row(
            InlineKeyboardButton(text="📋 Все тренировки", callback_data="all_workouts")
        )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data == "create_workout")
async def callback_create_workout(callback: CallbackQuery, state: FSMContext):
    """Start creating workout - select client"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    coach = await db.get_coach_by_telegram_id(user_id)
    clients = await db.get_clients_for_coach(coach['id'])
    
    if not clients:
        await callback.message.edit_text(
            "❌ У вас пока нет клиентов. Сначала добавьте клиента!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➕ Добавить клиента", callback_data="add_client"),
                InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")
            ]])
        )
        return
    
    await state.set_state(WorkoutStates.waiting_client)
    
    text = "👥 Выберите клиента для тренировки:"
    keyboard = InlineKeyboardBuilder()
    
    for client in clients:
        keyboard.row(
            InlineKeyboardButton(
                text=f"👤 {client['name']}", 
                callback_data=f"select_client_{client['id']}"
            )
        )
    
    keyboard.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="workouts")
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith("select_client_"), WorkoutStates.waiting_client)
async def client_selected(callback: CallbackQuery, state: FSMContext):
    """Client selected for workout"""
    await callback.answer()
    
    client_id = int(callback.data.split("_")[2])
    client = await db.get_client(client_id)
    
    await state.update_data(client_id=client_id, client_name=client['name'])
    
    # Quick workout creation
    tomorrow = datetime.now() + timedelta(days=1)
    workout_id = await db.create_workout(
        coach_id=(await db.get_coach_by_telegram_id(str(callback.from_user.id)))['id'],
        client_id=client_id,
        date=tomorrow,
        exercises=[],
        notes="Новая тренировка"
    )
    
    await state.clear()
    
    text = f"✅ Тренировка создана!\n\n👤 Клиент: {client['name']}\n📅 Дата: {tomorrow.strftime('%d.%m.%Y %H:%M')}\n💪 Упражнения: настройте в веб-приложении"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⚙️ Настроить упражнения", web_app=WebAppInfo(url=os.getenv('WEB_APP_URL', 'https://your-webapp-url.com')))
    )
    keyboard.row(
        InlineKeyboardButton(text="💪 Тренировки", callback_data="workouts"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

# Statistics
@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    """Show statistics"""
    await callback.answer()
    
    user_id = str(callback.from_user.id)
    coach = await db.get_coach_by_telegram_id(user_id)
    
    if not coach:
        await callback.message.answer("❌ Ошибка: тренер не найден")
        return
    
    stats = await db.get_stats_for_coach(coach['id'])
    
    text = f"""
📊 Статистика

👥 Клиенты: {stats['clients_count']}
💪 Всего тренировок: {stats['workouts_count']}
✅ Завершено: {stats['completed_workouts']}
📈 Процент завершения: {(stats['completed_workouts'] / max(stats['workouts_count'], 1) * 100):.1f}%

🗓️ Дата регистрации: {coach['created_at'].strftime('%d.%m.%Y')}
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="📈 Детальная статистика", web_app=WebAppInfo(url=os.getenv('WEB_APP_URL', 'https://your-webapp-url.com')))
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

# Help command
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help information"""
    text = """
🤖 Coach Assistant - Помощь

📋 Основные команды:
/start - Главное меню
/help - Эта справка

🎯 Возможности:
• 👥 Управление клиентами
• 💪 Планирование тренировок
• 📊 Статистика и отчеты
• 🌐 Веб-приложение для детального управления

💡 Используйте кнопки меню для быстрого доступа к функциям!
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    await message.answer(text, reply_markup=keyboard.as_markup())
