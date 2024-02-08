import time
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from brightestBio.common_utils import wait_for_element
from brightestBio.pages.common import CommonOps
from faker import Faker


class ScansPage(CommonOps):
    scan_view_option = (By.XPATH, "(//div/button[contains(text(),'View')])[1]")
    scan_details_name = (By.XPATH, "//span[contains(text(),'Name')]")
    scan_details_id = (By.XPATH, "//span[contains(text(),'ID')]")
    scan_details_date = (By.XPATH, "//span[contains(text(),'Date')]")
    scan_details_reader = (By.XPATH, "//span[contains(text(),'Reader')]")
    scan_details_status = (By.XPATH, "//span[contains(text(),'Status')]")
    scan_settings_button = (By.XPATH, "//button[@aria-label='configure']")
    scan_id_checkbox = (By.XPATH, "//input[@aria-labelledby='id']")
    next_button = (By.XPATH, "//button[contains(text(), 'Next')]")
    plate_barcode_field = (By.ID, "plate-barcode")
    scan_name_field = (By.ID, "scan-name")
    reader_dropdown = (By.XPATH, "//div[@tabindex=0]")
    create_now_button = (By.XPATH, "//button[contains(@class, 'MuiButton-root') and contains(@class, 'MuiButton-outlined') and contains(text(), 'Create New')]")
    error_message = (By.ID, "plate-barcode-helper-text")
    dropdown_value = (By.XPATH, "//div//ul/li[@tabindex=0]")
    select_all_button = (By.XPATH, "//button[contains(text(), 'Select All')]")
    clear_all_button = (By.XPATH, "//button[contains(text(), 'Clear Plate')]")
    create_button_review_page = (By.XPATH, "//button[contains(text(), 'Create')]")
    CREATED_SCAN_NAME = (By.XPATH, "//h1[@class='MuiTypography-root MuiTypography-h4 css-dsoyff']")
    REVIEW_PAGE_TITLE = (By.CSS_SELECTOR, 'h2.MuiTypography-root.MuiTypography-body1.MuiTypography-gutterBottom.css-n28fgj')
    barcode_info_locator = (By.CSS_SELECTOR, '.MuiPaper-root.MuiCard-root.css-1x76cf0 .MuiTypography-root.MuiTypography-subtitle2.MuiTypography-gutterBottom.css-1fwspuj')
    fill_attribute = (By.XPATH, "//div[@class='well mantine-125tskf 2-A']//*[name()='svg']/*[name()='path'][2]")
    back_to_dashboard_button = (By.XPATH, "//button[contains(text(), 'Back to Dashboard')]")
    scans_table_locator = (By.CLASS_NAME, 'MuiTable-root')
    rows_locator = (By.XPATH, '//table[@aria-label="View Scans"]/tbody/tr')
    first_scan_name_locator = (By.XPATH, '//table[@aria-label="View Scans"]/tbody/tr[1]/td[1]/div')
    delete_button_locator = (By.XPATH, '//table[@aria-label="View Scans"]/tbody/tr[1]/td[8]')

    def click_view_scan_option(self):
        self.wait_for(self.scan_view_option).click()

    def is_name_column_visible(self):
        return self.find(self.scan_details_name).is_displayed()

    def is_id_column_visible(self):
        return self.find(self.scan_details_id).is_displayed()

    def is_date_column_visible(self):
        return self.find(self.scan_details_date).is_displayed()

    def is_reader_column_visible(self):
        return self.find(self.scan_details_reader).is_displayed()

    def is_status_column_visible(self):
        return self.find(self.scan_details_status).is_displayed()

    def click_on_settings_button(self):
        self.find(self.scan_settings_button).click()
        time.sleep(1)

    def click_on_id_checkbox(self):
        self.find(self.scan_id_checkbox).click()

    def is_id_displayed(self):
        try:
            self.find(self.scan_details_id).is_displayed()
            return True
        except:
            return False

    def initiate_scan_creation(self):
        self.find(self.create_now_button).click()

    def next_button_enabled(self):
        next_button_element = self.find(self.next_button)
        return not next_button_element.get_attribute("disabled")

    def enter_valid_barcode(self, barcode):
        self.type_text(self.plate_barcode_field, barcode)
        self.click(self.next_button)

    def blank_barcode(self):
        self.type_text(self.plate_barcode_field, "")

    def check_bar_code_details(self, barcode):
        self.type_text(self.plate_barcode_field, barcode)

    def enter_invalid_barcode(self, in_valid_barcode):
        self.type_text(self.plate_barcode_field, in_valid_barcode)

    def enter_scan_name(self, scan_name):
        self.type_text(self.scan_name_field, scan_name)

    def get_invalid_barcode_message(self):
        return self.wait_for(self.error_message).is_displayed()

    def select_reader(self):
        self.find(self.reader_dropdown).click()
        self.find(self.dropdown_value).click()

    @staticmethod
    def generate_random_scan_name():
        fake = Faker()
        return "test" + str(fake.random_int(100, 999))

    def click_select_all_button(self):
        self.click(self.select_all_button)

    def click_on_next_button(self):
        self.find(self.next_button).click()

    def click_clear_all_button(self):
        self.click(self.clear_all_button)

    def click_on_create_under_review_page(self):
        self.find(self.create_button_review_page).click()

    def get_created_scan_name(self):
        return wait_for_element(self.driver, self.CREATED_SCAN_NAME).text

    def get_review_page_title(self):
        return wait_for_element(self.driver, self.REVIEW_PAGE_TITLE).text

    def select_well_option(self, row, column):
        well_locator = (By.XPATH, f"//div[@row='{row}' and @column='{column}']")
        well_element = self.driver.find_element(*well_locator)
        well_element.click()

    def verify_well_option_selected(self, row, column):
        well_locator = (By.XPATH, f"//div[@row='{row}' and @column='{column}' and contains(@class, 'selected')]")
        selected_well_element = self.driver.find_element(*well_locator)
        return selected_well_element.is_displayed()

    def select_well_option_with_shift(self, row, column):
        well_locator = (By.XPATH, f"//div[@row='{row}' and @column='{column}']")
        well_element = self.driver.find_element(*well_locator)
        action_chains = ActionChains(self.driver)
        action_chains.key_down(Keys.SHIFT).click(well_element).key_up(Keys.SHIFT).perform()

    def all_wall_point_selected(self):
        specific_element = self.find(self.fill_attribute)
        return specific_element.is_displayed()

    def click_back_to_dashboard_button(self):
        self.find(self.back_to_dashboard_button).click()

    def is_default_view_displaying_scans(self):
        scans_table_element = self.find_elements(*self.scans_table_locator)
        if not scans_table_element:
            return False
        rows = self.find_elements(*self.rows_locator)
        return len(rows) > 0

    def get_first_scan_name(self):
        return self.wait_for(self.first_scan_name_locator).text

    def click_delete_button(self):
        self.click(self.delete_button_locator)

    def is_scan_present(self, scan_name):
        xpath = f"//table[@aria-label='View Scans']//td[contains(text(), '{scan_name}')]"
        return self.is_element_present((By.XPATH, xpath))

