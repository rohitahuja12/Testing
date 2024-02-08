from selenium.webdriver.common.by import By
from brightestBio.pages.common import CommonOps


class DocumentPage(CommonOps):
    reader_view_option = (By.XPATH, "(//div/button[contains(text(),'View')])[5]")
    reader_title = (By.CSS_SELECTOR,
                    '.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.css-15j76c0 h1.MuiTypography-root.MuiTypography-h2.MuiTypography-gutterBottom.css-1sr95b5')

    def click_view_on_documents_option(self):
        self.wait_for(self.reader_view_option).click()

    def get_document_title_text(self):
        title_element = self.wait_for(self.reader_title)
        return title_element.text

    def verify_document_availability(self, document_name):
        document_locator = (By.XPATH,
                            f'//span[@class="MuiTypography-root MuiTypography-body1 MuiListItemText-primary css-uvxu54" and text()="{document_name}"]')
        try:
            self.driver.find_element(*document_locator)
            return True
        except:
            return False

    def is_sign_out_button_visible(self):
        sign_out_button_locator = (By.XPATH, '//button[contains(text(), "Sign Out")]')
        try:
            self.driver.find_element(*sign_out_button_locator)
            return True
        except:
            return False

    def is_profile_icon_visible(self):
        profile_icon_locator = (By.XPATH, '//button[@aria-label="profile"]')
        try:
            self.driver.find_element(*profile_icon_locator)
            return True
        except:
            return False