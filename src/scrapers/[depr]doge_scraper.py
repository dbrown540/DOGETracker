import logging
import time

from selenium import webdriver

from src.webdriver.webdriver import WebDriverSingleton
from settings import DOGE_SITE_URL

class DogeScraper:
    def __init__(self):
        self.driver: webdriver.Chrome = WebDriverSingleton.get_instance()

    @WebDriverSingleton.driver_get_retry
    def get_doge_site(self):
        """
        Retrieves the Doge site using the web driver.
        
        This method attempts to navigate the web driver to the specified Doge site URL. 
        If an error occurs during the navigation, it logs the error message.
        
        Raises:
            WebDriverException: If there is an issue with the web driver while trying to access the site.
        
        Returns:
            None
        """
        self.driver.get(DOGE_SITE_URL)
        time.sleep(5)

    
