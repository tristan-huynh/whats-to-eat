import json
import os
import asyncio
import logging
import schedule
import time
from datetime import datetime
from urllib.request import urlopen, Request
from threading import Thread

class MenuCacheManager:
    def __init__(self):
        self.cache_file = "src/cache/todays_menu.json"
        self.api_url = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self._running = False
        self._scheduler_thread = None

    def fetch_and_cache_menu(self):
        # Fetch menu data from API and save to cache file
        try:
            logging.info("Fetching menu data for cache update...")
            response = urlopen(Request(self.api_url, headers=self.headers))
            data = json.loads(response.read())
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # Save
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            logging.info(f"Menu cache updated successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logging.error(f"Failed to update menu cache: {e}")

    def load_cached_menu(self):
        # Load menu data from cache file
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            else:
                logging.warning("Cache file not found, fetching fresh data...")
                self.fetch_and_cache_menu()
                return self.load_cached_menu()
        except Exception as e:
            logging.error(f"Failed to load cached menu: {e}")
            return None

    def setup_schedule(self):
        # Schedule cache updates at 12 AM, 7 AM, 11 AM, and 3 PM
        schedule.every().day.at("00:00").do(self.fetch_and_cache_menu)
        schedule.every().day.at("07:00").do(self.fetch_and_cache_menu)
        schedule.every().day.at("11:00").do(self.fetch_and_cache_menu) 
        schedule.every().day.at("15:00").do(self.fetch_and_cache_menu)
        schedule.every().day.at("17:00").do(self.fetch_and_cache_menu)
        schedule.every().day.at("21:00").do(self.fetch_and_cache_menu)

        logging.info("Cache scheduler configured for 00:00, 07:00, 11:00, 15:00, 17:00, and 21:00 daily")

    def _run_scheduler(self):
        # Set to run in a thread
        while self._running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start_scheduler(self):
        # Start scheduling
        if not self._running:
            self._running = True
            self.setup_schedule()
            
            # Fetch initial cache if it doesn't exist
            if not os.path.exists(self.cache_file):
                logging.info("No cache file found, creating initial cache...")
                self.fetch_and_cache_menu()
            
            # Start scheduler in background thread
            self._scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
            self._scheduler_thread.start()
            logging.info("Menu cache scheduler started")

    def stop_scheduler(self):
        # Stop scheduler safely
        if self._running:
            self._running = False
            if self._scheduler_thread:
                self._scheduler_thread.join(timeout=5)
            logging.info("Menu cache scheduler stopped")

    def get_cache_info(self):
        if os.path.exists(self.cache_file):
            stat = os.stat(self.cache_file)
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            file_size = stat.st_size
            return {
                "exists": True,
                "last_modified": last_modified,
                "size_bytes": file_size,
                "next_scheduled_runs": [
                    "00:00 daily",
                    "07:00 daily",
                    "11:00 daily", 
                    "15:00 daily",
                    "17:00 daily",
                    "21:00 daily"
                ]
            }
        else:
            return {"exists": False}
