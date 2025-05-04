import sys
sys.dont_write_bytecode = True

import os
from dotenv import load_dotenv

from modules.bot_instance import bot
from modules.database import init_databases
from modules.handlers import register_all_handlers

# Load environment variables
load_dotenv()

def main():
    """Main function to initialize and start the bot"""
    # Initialize databases
    init_databases()
    
    # Register all handlers
    register_all_handlers()
    
    # Start the bot
    print("Bot started successfully!")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    main()