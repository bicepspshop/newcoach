#!/usr/bin/env python3
"""
Coach Assistant Bot - Main Entry Point
Simplified, compact implementation for coach management
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import db
from bot import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coach_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Include router
dp.include_router(router)


async def on_startup():
    """Actions on bot startup"""
    logger.info("🚀 Starting Coach Assistant Bot...")
    
    # Connect to database
    try:
        await db.connect()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Get bot info
    try:
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot started: @{bot_info.username}")
        logger.info(f"👤 Bot name: {bot_info.first_name}")
    except Exception as e:
        logger.error(f"❌ Failed to get bot info: {e}")
        raise
    
    # Set bot commands
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="❓ Помощь"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands set")


async def on_shutdown():
    """Actions on bot shutdown"""
    logger.info("🔄 Shutting down bot...")
    
    # Close database connection
    try:
        await db.disconnect()
        logger.info("✅ Database disconnected")
    except Exception as e:
        logger.error(f"❌ Database disconnect error: {e}")
    
    # Close bot session
    await bot.session.close()
    logger.info("✅ Bot shutdown complete")


async def main():
    """Main function"""
    try:
        await on_startup()
        
        logger.info("🏋️‍♂️ Coach Assistant Bot is ready!")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        raise
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
