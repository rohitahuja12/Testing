from brightestBio.pages.common import CommonOps
from selenium.webdriver.common.by import By


class TestLogoutPage(CommonOps):
    sign_out_button = (By.XPATH, "//button[contains(text(),'Sign Out')]")
    forgot_password = "//*[contains(text(), 'Forgot password?')]"

    def test_click_on_sign_out_button(self):
        self.wait_for(self.sign_out_button).is_displayed()
        self.wait_for(self.sign_out_button).click()
