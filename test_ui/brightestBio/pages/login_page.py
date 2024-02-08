import time
from selenium.webdriver.common.by import By
from brightestBio.pages.common import CommonOps


class TestLoginPage(CommonOps):
        def __init__(self, driver):
        super().__init__(driver)
    
    username_input = (By.ID, "username")
    password_input = (By.ID, "password")
    login_button = (By.XPATH, "(//button[@type='submit'])")
    empowerDashboard = "//*[contains(text(), 'Empower Dashboard')]"
    errorMessage = "//*[@id='error-element-password']"

    def enter_login_username(self, username):
        self.wait_for(self.username_input).is_enabled()
        self.wait_for(self.username_input).send_keys(username)

    def enter_login_password(self, password):
        self.wait_for(self.password_input).is_enabled()
        self.find(self.password_input).send_keys(password)

    def click_login_button(self):
        self.wait_for(self.login_button).is_enabled()
        self.find(self.login_button).click()

    def login_into_application(self, username, password):
        self.wait_for(self.username_input).is_enabled()
        self.wait_for(self.username_input).send_keys(username)
        self.wait_for(self.password_input).is_enabled()
        self.find(self.password_input).send_keys(password)
        self.wait_for(self.login_button).is_enabled()
        self.find(self.login_button).click()
        time.sleep(5)
