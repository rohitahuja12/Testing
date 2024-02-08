from selenium.webdriver.common.by import By
from brightestBio.pages.common import CommonOps


class ReaderPage(CommonOps):
    reader_view_option = (By.XPATH, "(//div/button[contains(text(),'View')])[4]")
    reader_title = (By.CSS_SELECTOR, '.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.css-15j76c0 h1.MuiTypography-root.MuiTypography-h2.MuiTypography-gutterBottom.css-1sr95b5')
    reader_table_locator = (By.CLASS_NAME, 'MuiTable-root')
    rows_locator = (By.XPATH, '//table[@aria-label="Readers"]/tbody/tr')
    reader_details_serial_number = (By.XPATH, "//span[contains(text(),'Serial')]")
    reader_details_door = (By.XPATH, "//span[contains(text(),'Door')]")

    def click_view_on_reader_option(self):
        self.wait_for(self.reader_view_option).click()

    def get_reader_title_text(self):
        title_element = self.wait_for(self.reader_title)
        return title_element.text

    def is_default_view_displaying_reader(self):
        scans_table_element = self.find_elements(*self.reader_table_locator)
        if not scans_table_element:
            return False
        rows = self.find_elements(*self.rows_locator)
        return len(rows) > 0

    def is_serial_number_column_visible_under_reader_module(self):
        return self.find(self.reader_details_serial_number).is_displayed()

    def is_door_column_visible_under_reader_module(self):
        return self.find(self.reader_details_door).is_displayed()
