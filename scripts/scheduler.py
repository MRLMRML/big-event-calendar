"""6-hour cron scheduler for automated scraping."""

import time
import signal
import sys
from datetime import datetime
from scripts.scraper import scrape_all
from scripts.utils import logger, load_config


class Scheduler:
    def __init__(self):
        self.config = load_config().get("scheduler", {})
        self.interval = self.config.get("interval_hours", 6) * 3600
        self.running = True

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info("Shutdown signal received, stopping scheduler...")
        self.running = False

    def run_once(self):
        logger.info("Starting scheduled scrape...")
        start = time.time()
        try:
            stats = scrape_all()
            elapsed = time.time() - start
            logger.info(f"Scrape completed in {elapsed:.1f}s: {stats}")
        except Exception as e:
            logger.error(f"Scheduled scrape failed: {e}")

    def run_forever(self):
        logger.info(f"Scheduler started, interval: {self.interval // 3600}h")
        self.run_once()

        while self.running:
            next_run = datetime.now().timestamp() + self.interval
            logger.info(f"Next scrape at: {datetime.fromtimestamp(next_run).isoformat()}")

            while self.running and time.time() < next_run:
                time.sleep(60)

            if self.running:
                self.run_once()

        logger.info("Scheduler stopped")


if __name__ == "__main__":
    scheduler = Scheduler()
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        scheduler.run_once()
    else:
        scheduler.run_forever()
