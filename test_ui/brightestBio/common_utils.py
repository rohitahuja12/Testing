from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

DEFAULT_TIMEOUT = 10


def wait_for_element(driver: WebDriver, locator, timeout=DEFAULT_TIMEOUT):
    try:
        print(f"Waiting for element with locator: {locator}")
        element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
        return element
    except TimeoutException:
        raise TimeoutException(f"Timed out waiting for element {locator} to be visible")
