from telnetlib import EC
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains


class CommonOps:
    def __init__(self, driver):
        self.driver = driver
        self._wait = WebDriverWait(self.driver, 10)
        self._action = ActionChains(self.driver)

    def wait_for(self, locator):
        return self._wait.until(ec.presence_of_element_located(locator))

    def find(self, locator):
        return self.driver.find_element(*locator)

    def click(self, locator):
        self.find(locator).click()

    def context_click(self, element):
        return self._action.context_click(element)

    def alert(self):
        return self._wait.until(ec.alert_is_present())

    def type_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def select_dropdown_option(self, locator, option_text):
        dropdown = self.find(locator)
        dropdown.click()
        option_locator = (By.XPATH, f"//div[@role='option'][contains(text(), '{option_text}')]")
        self.click(option_locator)

    def select_dropdown_option_by_index(self, locator, index):
        dropdown = Select(self.find(locator))
        dropdown.select_by_index(index)

    def is_element_present(self, locator):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
            return True
        except:
            return False

    def find_elements(self, by, value, timeout=10):
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except Exception as e:
            print(f"Error finding elements: {e}")
            return []
