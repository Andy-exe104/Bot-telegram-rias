#!/usr/bin/env python3
"""
Simple debug script to capture any startup errors
This runs before main.py to ensure we capture all errors
"""

import os
import sys
import traceback
from datetime import datetime

def write_debug_log(message, error=None):
    """Write debug information to file"""
    try:
        with open('debug_log.txt', 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")
            if error:
                f.write(f"Error: {str(error)}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
            f.write("-" * 50 + "\n")
            f.flush()  # Force write to disk
    except Exception as e:
        print(f"Could not write debug log: {e}")

def check_environment():
    """Check environment variables"""
    write_debug_log("Starting environment check...")
    
    # Check if we can write files
    try:
        with open('test_write.txt', 'w') as f:
            f.write('test')
        os.remove('test_write.txt')
        write_debug_log("File write test: SUCCESS")
    except Exception as e:
        write_debug_log("File write test: FAILED", e)
    
    # Check environment variables
    env_vars = ['BOT_TOKEN', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            write_debug_log(f"Environment variable {var}: SET ({value[:10]}...)")
        else:
            write_debug_log(f"Environment variable {var}: NOT SET")

def check_imports():
    """Check if we can import required modules"""
    write_debug_log("Starting import check...")
    
    try:
        import asyncio
        write_debug_log("Import asyncio: SUCCESS")
    except Exception as e:
        write_debug_log("Import asyncio: FAILED", e)
    
    try:
        import dotenv
        write_debug_log("Import dotenv: SUCCESS")
    except Exception as e:
        write_debug_log("Import dotenv: FAILED", e)
    
    try:
        from telegram import Bot
        write_debug_log("Import telegram: SUCCESS")
    except Exception as e:
        write_debug_log("Import telegram: FAILED", e)
    
    try:
        import aiomysql
        write_debug_log("Import aiomysql: SUCCESS")
    except Exception as e:
        write_debug_log("Import aiomysql: FAILED", e)

def main():
    """Main debug function"""
    write_debug_log("=" * 50)
    write_debug_log("DEBUG SCRIPT STARTED")
    write_debug_log("=" * 50)
    
    # Check environment
    check_environment()
    
    # Check imports
    check_imports()
    
    # Try to run main.py
    write_debug_log("Attempting to run main.py...")
    try:
        import main
        write_debug_log("Import main.py: SUCCESS")
    except Exception as e:
        write_debug_log("Import main.py: FAILED", e)
    
    write_debug_log("DEBUG SCRIPT COMPLETED")

if __name__ == "__main__":
    main()