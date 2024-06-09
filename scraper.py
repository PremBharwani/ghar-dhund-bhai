"""
Scraper class: Responsible for scraping and other utils
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Setup logging 
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Scraper():
    
    WAIT_DURATION = 10 # Seconds to wait for the element to appear
    N_TRIES = 5

    def __init__(self):
        self.driver = None

    def initDriver(self, is_headless = False):
        # Initialize a firefox driver
        logging.info("Initializing web driver")
        options = webdriver.FirefoxOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        ####################
        options.set_preference("pdfjs.disabled", True) # To disable the firefox browsers default action to open the PDF files.
        if is_headless:
            options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)

    def __validateInitialization(self):
        if(self.driver is None):
            logging.error("Web driver is not initialized. Run initDriver() method first.")
            raise Exception("Web driver is not initialized. Run initDriver() method first.")
    
    def navigateToUrl(self, url):
        """
        Navigates to the url mentioned
        """
        logger.debug("navigateToUrl ", url)
        self.driver.get(url)

    def findElem(self, by_method, by_value):
        """
        Searches for the element in the DOM by using 'by_value' & 'by_method'
        Returns: 'elem' if the element is found. 'None' otherwise.
        """
        self.__validateInitialization()
        try:
            elem = self.driver.find_element(by_method, by_value) 
        except:
            elem = None
        logging.debug(f"findElem returned {type(elem)}")
        return elem

    def findElemWhenVisible(self, by_method, by_value):
        """
        find the element when visible, wait for WAIT_DURATION
        """
        self.__validateInitialization()
        try:
            elem =  WebDriverWait(self.driver, self.WAIT_DURATION).until(EC.presence_of_element_located((by_method, by_value)))
        except:
            elem = None
        logging.debug(f"findElemWhenVisible returned {type(elem)}")
        return elem

    def findElemWhenClickable(self, by_method, by_value):
        """
        find the element when clickable, wait for WAIT_DURATION
        """
        self.__validateInitialization()
        try:
            elem =  WebDriverWait(self.driver, self.WAIT_DURATION).until(EC.element_to_be_clickable((by_method, by_value)))
        except:
            elem = None
        logging.debug(f"findElemWhenClickable returned {type(elem)}")
        return elem

    def refreshPage(self):
        """
        refresh the current page
        """
        self.driver.refresh()

    def waitUntilElemAppears(self, by_method, by_value, refresh_if_not_found = False):
        """
        waitUntilElemAppears waits for self.WAIT_DURATION seconds until the target elem is visible. If refresh_if_not_found is set & target elem is not found at the end of an attempt, the page is refreshed. self.N_TRIES such attempts are made.

        Note: This method returns only if the element is found. Else throws an error.
        """
        n_tries = self.N_TRIES
        while n_tries>0:
            n_tries-=1
            elem = self.findElemWhenVisible(by_method, by_value)
            if elem is None: # Couldn't find the element
                logger.info(f"waitUntilElemAppears: could not locate elem. attempt {n_tries+1}/{self.N_TRIES} | {by_method=} | {by_value=}")
                if refresh_if_not_found:
                    self.refreshPage()
            else:
                logger.info(f"waitUntilElemAppears: DONE locating elem. in attempt {n_tries+1}/{self.N_TRIES} | {by_method=} | {by_value=}")
                return
        logger.error(f"waitUntilElemAppears: Could NOT locate elem. in {self.N_TRIES} attempts | {by_method=} | {by_value=}")
        raise Exception(f"waitUntilElemAppears: Could NOT locate elem. in {self.N_TRIES} attempts | {by_method=} | {by_value=}")


if __name__=="__main__":
    s = Scraper()
    s.initDriver()
    s.navigateToUrl("https://facebook.com")
    import time
    time.sleep(10)
    s.refreshPage()

    
