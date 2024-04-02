import threading
import time
from custom_logs.models import custom_log
from scrapers.views import scrapers_main_function


class ScrapersMainFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        active_threads = threading.enumerate()
        threads_name_list = []
        for thread in active_threads:
            if thread.is_alive():
                threads_name_list.append(str(thread.name))
        if not 'scraper_functions_thread' in threads_name_list:
            custom_log("scraper_functions_thread: start ScrapersFunctionThread", f"scrapers")
            ScrapersFunctionThread(name='scraper_functions_thread').start()
            time.sleep(1)
        return


class ScrapersFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log("ScrapersFunctionThread: start thread", f"scrapers")
        while True:
            try:
                custom_log("scrapers_function: has been started", f"scrapers")
                scrapers_main_function()
                custom_log("scrapers_function: has been finished. waiting for 5 seconds", f"scrapers")
            except Exception as e:
                custom_log(f"scrapers_function: try/except-> err: {str(e)}. waiting for 5 seconds", f"scrapers")
            time.sleep(5)