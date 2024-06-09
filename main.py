import os
from selenium.webdriver.common.by import By
import time
import logging
from dotenv import load_dotenv
import scraper
import sys
import fb

URL = "https://facebook.com"
GROUP_ID = "320292845738195"

# Setup logging 
# Defining handlers
fhandler = logging.FileHandler(filename="tmp.log")
shandler = logging.StreamHandler(stream=sys.stdout)
handlers = [fhandler, shandler]

logging.basicConfig(
    level = logging.INFO,     
    format = '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers = handlers
)

def main():
    s = scraper.Scraper()
    s.initDriver()
    fb.login(s)
    fb.scrapeGroup(s, GROUP_ID)

if __name__ == "__main__":
    # main()
    main()




