from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from brightestBio.pages.common import CommonOps


class AnalysesPage(CommonOps):
    analysis_templates_view_option = (By.XPATH, "(//div/button[contains(text(),'View')])[3]")
    TITLE_LOCATOR = (By.CSS_SELECTOR, '.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.css-15j76c0 h1.MuiTypography-root.MuiTypography-h2.MuiTypography-gutterBottom.css-1sr95b5')
    analyses_name_checkbox = (By.XPATH, "//input[@aria-labelledby='name']")
    analyses_page_name_list = (By.XPATH, "//span[contains(text(),'Name')]")
    analyses_table_locator = (By.CLASS_NAME, 'MuiTable-root')
    rows_locator = (By.XPATH, '//table[@aria-label="View Results"]/tbody/tr')
    search_input_field = (By.ID, "search-textbox-basic")
    next_page_button_locator = (By.XPATH, "//button[contains(@class, 'MuiIconButton-root') and contains(@aria-label, 'Go to next page')]")
    analysis_template_section = (By.XPATH, "//div[contains(@class, 'MuiTypography-h5') and text()='Analysis Templates']")
    back_button = (By.XPATH, "(//button[contains(text(), 'Back')])[2]")
    scan_section = (By.XPATH, "//div[contains(@class, 'MuiTypography-h5') and text()='Scans']")
    input_field_locator = (By.XPATH, "//input[@aria-invalid='false']")

    def click_view_on_analyses_option(self):
        self.wait_for(self.analysis_templates_view_option).click()

    def get_analyses_title_text(self):
        title_element = self.wait_for(self.TITLE_LOCATOR)
        return title_element.text

    def click_on_name_checkbox_under_setting_icon(self):
        self.find(self.analyses_name_checkbox).click()

    def is_name_column_visible__analysis_template_module(self):
        try:
            self.find(self.analyses_page_name_list).is_displayed()
            return True
        except:
            return False

    def is_default_view_displaying_analyses(self):
        scans_table_element = self.find_elements(*self.analyses_table_locator)
        if not scans_table_element:
            return False
        rows = self.find_elements(*self.rows_locator)
        return len(rows) > 0

    def search_analysis(self, analysis_name):
        search_input = self.driver.find_element(By.ID, "search-textbox-basic")
        search_input.clear()
        search_input.send_keys(analysis_name)
        search_input.send_keys(Keys.RETURN)

    def verify_search_results(self, search_term):
        wait = WebDriverWait(self.driver, 10)
        table_locator = (By.XPATH, "//table[@aria-label='View Results']")
        wait.until(EC.presence_of_element_located(table_locator))

        rows_locator = (By.XPATH, "//table[@aria-label='View Results']/tbody/tr")
        rows = self.driver.find_elements(*rows_locator)

        for row in rows:
            row_text = row.text
            print(f"Actual Row Content: {row_text}")

            assert search_term.lower() in row_text.lower(), f"Search term '{search_term}' not found in row: {row_text}"

    def get_scans_rows(self):
        return self.driver.find_elements(By.XPATH, '//table[@aria-label="Scans"]/tbody/tr')

    @staticmethod
    def get_status_of_scan(row):
        status_locator = './/td[5]'
        return row.find_element(By.XPATH, status_locator).text

    @staticmethod
    def is_scan_select_disabled(row):
        radio_button_locator = './/td[1]/div/div/span'
        return 'disabled' in row.find_element(By.XPATH, radio_button_locator).get_attribute('class')

    @staticmethod
    def select_scan(row):
        radio_button_locator = './/td[1]/div/div/span'
        row.find_element(By.XPATH, radio_button_locator).click()

    def click_go_to_next_page_button(self):
        self.find(self.next_page_button_locator).click()

    def is_analysis_templates_section_displayed(self):
        return self.find(self.analysis_template_section).is_displayed()

    def click_on_back_button(self):
        self.find(self.back_button).click()

    def is_scans_section_displayed(self):
        return self.find(self.scan_section).is_displayed()

    def find_input_field(self):
        return self.driver.find_element(*self.input_field_locator)

    def get_analysis_rows(self):
        return self.driver.find_elements(By.XPATH, '//table[@aria-label="Analysis Templates"]/tbody/tr')