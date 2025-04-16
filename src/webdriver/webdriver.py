"""
WebDriver Singleton Module
==========================

This module provides a singleton implementation for managing Selenium WebDriver instances.

The singleton pattern ensures that only one WebDriver instance is created and reused
throughout the application, which helps with resource management and prevents
unnecessary browser instances from being spawned.

Classes:
    WebDriverSingleton: A singleton class that manages a Chrome WebDriver instance.

Methods:
    WebDriverSingleton.get_instance(): Returns the existing WebDriver 
    instance or creates a new one.
    WebDriverSingleton.close_instance(): Closes the WebDriver instance if it exists.

Usage:
    driver = WebDriverSingleton.get_instance()
    # Use the driver for web automation tasks
    WebDriverSingleton.close_instance()  # Close when done
"""
import time
from typing import Optional, ClassVar, Callable
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

from settings import MAX_RETRIES, RETRY_TIMEOUT

logging.getLogger(__file__)

class WebDriverSingleton:
    """
    A singleton class to manage a single instance of a Selenium WebDriver.
    
    This class ensures that only one instance of the WebDriver is created and
    reused throughout the application, optimizing resource usage.
    
    Attributes:
        _instance (webdriver.Chrome): The singleton instance of the Chrome WebDriver.
    """
    _instance: ClassVar[Optional[webdriver.Chrome]] = None

    @classmethod
    def get_instance(cls) -> webdriver.Chrome:
        """
        Creates and returns the singleton instance of the WebDriver.
        
        If the WebDriver instance doesn't exist, it creates a new one with
        specific configuration options. If it already exists, it returns
        the existing instance.
        
        Returns:
            webdriver.Chrome: The singleton instance of the Chrome WebDriver.
        """
        if cls._instance is None:
            # Define driver options
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument('--disable-extensions')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Define service options
            chromedriver_path = r"chromedriver-mac-arm64/chromedriver"
            service = Service(executable_path=chromedriver_path)

            # Create driver instance
            cls._instance = webdriver.Chrome(options=options, service=service)
        return cls._instance

    @classmethod
    def close_instance(cls) -> None:
        """
        Closes the WebDriver instance if it exists.
        
        This method quits the WebDriver instance and sets the singleton
        instance to None, allowing for a new instance to be created if needed.
        """
        if cls._instance is not None:
            cls._instance.quit()
            cls._instance = None

    @staticmethod
    def driver_get_retry(func: Callable):
        """
        Decorator to retry a function call in case of a TimeoutException.
        
        This decorator attempts to call the decorated function multiple times 
        if a TimeoutException is raised. It logs the success and failure of each 
        attempt and waits for a specified timeout period before retrying.
        
        Args:
            func (Callable): The function to be decorated and retried.
        
        Returns:
            Callable: The wrapped function that includes retry logic.
        
        Raises:
            TimeoutException: If the function fails to execute successfully 
            after the maximum number of retries.
            
        Logs:
            - Info: Successful access to the site.
            - Warning: Timeout error details and retry attempts.
            - Error: Failure to access the site after all retries.
        """
        def wrapper(*args, **kwargs):
            for attempt in range(MAX_RETRIES):
                try:
                    result = func(*args, **kwargs)
                    logging.info(
                        "Successfully accessed the site for %s in %d attempts!",
                        func.__name__, attempt + 1
                    )
                    return result
                except TimeoutException:
                    logging.warning(
                        "Received a timeout error during driver.get() in %s. "
                        "Retrying in %d seconds... (Attempt %d of %d)",
                        func.__name__, RETRY_TIMEOUT, attempt + 1, MAX_RETRIES
                    )
                    time.sleep(RETRY_TIMEOUT)
            logging.error(
                "Failed to get the site in %s after %d retries.", 
                func.__name__, MAX_RETRIES
            )
            raise TimeoutException(
                f"{func.__name__} failed after {MAX_RETRIES} retry attempts."
            )
        return wrapper
