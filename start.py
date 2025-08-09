#!/usr/bin/env python3
"""
Simple startup script for Railway
This will capture any errors and then start the bot
"""

import os
import sys
import traceback
from datetime import datetime

def log_error(message, error=None):
    """Log error to file"""
    try:
        with open('railway_errors.txt', 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")
            if error:
                f.write(f"Error: {str(error)}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
            f.write("=" * 50 + "\n")
            f.flush()
    except Exception as e:
        print(f"Could not write error log: {e}")

def main():
    """Main startup function"""
    print("🚀 Starting Rias Gremory Bot...")
    
    # Log startup
    log_error("RAILWAY STARTUP - Bot initialization started")
    
    # Check environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        log_error("CRITICAL ERROR: BOT_TOKEN not found in environment variables")
        print("❌ BOT_TOKEN not found!")
        return
    
    print(f"✅ BOT_TOKEN found: {bot_token[:10]}...")
    
    # Check database variables
    db_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    for var in db_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log_error(f"WARNING: Missing database variables: {missing_vars}")
        print(f"⚠️ Missing database variables: {missing_vars}")
    
    # Try to import and run main
    try:
        print("🔧 Importing main module...")
        import main
        print("✅ Main module imported successfully")
        log_error("SUCCESS: Main module imported")
        
        # Run the bot
        print("🚀 Starting bot...")
        import asyncio
        asyncio.run(main.main())
        
    except Exception as e:
        log_error("CRITICAL ERROR: Failed to start bot", e)
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()