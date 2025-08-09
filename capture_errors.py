#!/usr/bin/env python3
"""
Error capture script that saves all errors to a file for GitHub
This will capture everything and save it automatically
"""

import os
import sys
import traceback
import logging
from datetime import datetime

# Set up logging to capture everything
def setup_error_capture():
    """Setup error capture for all errors"""
    
    # Create a log file that will be committed to git
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('github_errors.txt', mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Capture uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # Log startup
    logging.info("=" * 60)
    logging.info("ERROR CAPTURE SYSTEM STARTED")
    logging.info("=" * 60)

def capture_console_output():
    """Capture all console output"""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    class TeeOutput:
        def __init__(self, original_stream):
            self.original_stream = original_stream
            self.log_file = open('github_errors.txt', 'a', encoding='utf-8')
        
        def write(self, text):
            self.original_stream.write(text)
            self.log_file.write(text)
            self.log_file.flush()
        
        def flush(self):
            self.original_stream.flush()
            self.log_file.flush()
    
    sys.stdout = TeeOutput(original_stdout)
    sys.stderr = TeeOutput(original_stderr)

def main():
    """Main function to capture all errors"""
    # Setup error capture
    setup_error_capture()
    
    # Capture console output
    capture_console_output()
    
    # Log environment info
    logging.info("Environment check:")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Platform: {sys.platform}")
    logging.info(f"Working directory: {os.getcwd()}")
    
    # Check environment variables
    env_vars = ['BOT_TOKEN', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            logging.info(f"Environment variable {var}: SET ({value[:10]}...)")
        else:
            logging.warning(f"Environment variable {var}: NOT SET")
    
    # Try to run the main bot
    try:
        logging.info("Attempting to import and run main bot...")
        import start
        start.main()
    except Exception as e:
        logging.error(f"Failed to run bot: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    main()