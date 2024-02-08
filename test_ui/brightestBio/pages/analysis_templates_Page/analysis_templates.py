from faker import Faker
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from brightestBio.common_utils import wait_for_element
from brightestBio.pages.common import CommonOps


class AnalysisTemplatesPage(CommonOps, ):
    analysis_templates_view_option = (By.XPATH, "(//div/button[contains(text(),'View')])[2]")
    TITLE_LOCATOR = (By.CSS_SELECTOR, '.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.css-15j76c0 h1.MuiTypography-root.MuiTypography-h2.MuiTypography-gutterBottom.css-1sr95b5')
    analysis_templates_details_product = (By.XPATH, "//span[contains(text(),'Product')]")
    analysis_templates_details_protocol = (By.XPATH, "//span[contains(text(),'Protocol')]")
    analysis_templates_protocol_checkbox = (By.XPATH, "//input[@aria-labelledby='protocol']")
    analysis_templates_table_locator = (By.CLASS_NAME, 'MuiTable-root')
    rows_locator = (By.XPATH, '//table[@aria-label="Analysis Templates"]/tbody/tr')
    PRODUCT_CARD = (By.CSS_SELECTOR, '.MuiGrid-root.MuiGrid-item.css-1etv89n')
    analysis_templates_name_field = (By.ID, "template-name")
    first_analysis_template_name_locator = (By.XPATH, '//table[@aria-label="Analysis Templates"]/tbody/tr[1]/td[1]/div')
    create_now_button = (By.XPATH, "//button[contains(text(), 'Create New')]")
    delete_button_locator = (By.XPATH, '//table[@aria-label="Analysis Templates"]/tbody/tr[1]/td[5]')
    first_scan_name_locator = (By.XPATH, '//table[@aria-label="View Scans"]/tbody/tr[1]/td[1]/div')
    REVIEW_PAGE_TITLE = (By.CSS_SELECTOR, 'div.analysis-template-creation-steps h2.css-n28fgj + h2.css-1xy0hka')
    STANDARD_DILUTION_FACTOR_INPUT = (By.CLASS_NAME, "MuiInputBase-input")
    error_message_under_standard_dilution_page = (By.XPATH, '//*[@id="standard-dilution-factor-helper-text"]')
    PLATE_MAP_DROPDOWN = (By.ID, "plate-maps")
    PLATE_MAP_OPTIONS = (By.CSS_SELECTOR, "ul[aria-labelledby='plate-maps-label'] li")
    alphanumeric_element = (By.XPATH, "//div[@class='well mantine-atnmxm 2-A']//*[name()='svg']")
    fill_attribute = (By.XPATH, "//div[@class='well mantine-atnmxm 2-A']//*[name()='svg']/*[name()='path'][2]")
    context_menu_option_make_standard = (By.XPATH, "//button[contains(text(), 'Make Standard')]")
    context_menu_option_make_unknown = (By.XPATH, "//button[contains(text(), 'Make Unknown')]")
    context_menu_option_make_blank = (By.XPATH, "//button[contains(text(), 'Make Blank')]")
    context_menu_option_make_empty = (By.XPATH, "//button[contains(text(), 'Make Empty')]")
    context_menu_option_edit_well = (By.XPATH, "//button[contains(text(), 'Edit Well')]")
    clear_plate_button = (By.CLASS_NAME, "css-11aoeco")
    input_field_under_edit_well_option = (By.XPATH, "(//input[contains(@class, 'mantine-TextInput-input')])[2]")
    save_button_under_edit_well = (By.CLASS_NAME, "mantine-Button-label")
    input_field_placeholder = "A2"  # Adjust this value based on your actual placeholder value
    input_field_after_save = (By.XPATH, f'//input[contains(@placeholder, "{input_field_placeholder}")]')
    wall_point_a_locator = (By.XPATH, "//div[@class='MuiBox-root css-0']//p[text()='A']")

    def click_view_analysis_templates_option(self):
        self.wait_for(self.analysis_templates_view_option).click()

    def get_analysis_template_title_text(self):
        title_element = self.wait_for(self.TITLE_LOCATOR)
        return title_element.text

    def is_product_column_visible_under_analysis_template_module(self):
        return self.find(self.analysis_templates_details_product).is_displayed()

    def click_on_protocol_checkbox_under_setting_icon(self):
        self.find(self.analysis_templates_protocol_checkbox).click()

    def is_protocol_column_visible__analysis_template_module(self):
        try:
            self.find(self.analysis_templates_details_protocol).is_displayed()
            return True
        except:
            return False

    def is_default_view_displaying_analysis_templates(self):
        scans_table_element = self.find_elements(*self.analysis_templates_table_locator)
        if not scans_table_element:
            return False
        rows = self.find_elements(*self.rows_locator)
        return len(rows) > 0

    def get_product_cards(self):
        return self.driver.find_elements(*self.PRODUCT_CARD)

    def get_product_card(self, index):
        product_cards = self.driver.find_elements(*self.PRODUCT_CARD)
        if 0 <= index < len(product_cards):
            product_cards[index].click()
        else:
            raise ValueError(f"Invalid index: {index}. Index should be between 0 and {len(product_cards) - 1}.")

    def enter_analysis_templates_name(self, analysis_templates_name):
        self.type_text(self.analysis_templates_name_field, analysis_templates_name)

    @staticmethod
    def generate_random_name():
        fake = Faker()
        return "test" + str(fake.random_int(100, 999))

    def get_first_analysis_templates_name(self):
        return self.wait_for(self.first_analysis_template_name_locator).text

    def click_on_create_now_button(self):
        self.find(self.create_now_button).click()

    def select_context_menu_option(self, option):
        if option == 'Make Standard':
            context_menu_option = self.context_menu_option_make_standard
        elif option == 'Make Unknown':
            context_menu_option = self.context_menu_option_make_unknown
        elif option == 'Make Blank':
            context_menu_option = self.context_menu_option_make_blank
        elif option == 'Make Empty':
            context_menu_option = self.context_menu_option_make_empty
        elif option == 'Edit Well':
            context_menu_option = self.context_menu_option_edit_well
        else:
            raise ValueError(f"Invalid context menu option: {option}")

        option_element = self.driver.find_element(*context_menu_option)
        option_element.click()

    def perform_right_click_and_select_option(self, option):
        alphanumeric_element = self.driver.find_element(*self.alphanumeric_element)
        action_chains = ActionChains(self.driver)
        action_chains.context_click(alphanumeric_element).perform()
        self.driver.implicitly_wait(5)
        self.select_context_menu_option(option)

    def get_svg_fill_attribute(self):
        svg_path = self.driver.find_element(*self.fill_attribute)
        return svg_path.get_attribute('fill')

    def select_plate_map_option(self):
        plate_map_dropdown = self.driver.find_element(*self.PLATE_MAP_DROPDOWN)
        plate_map_dropdown.click()

    def click_plate_map_option(self, option_text):
        option_locator = (By.XPATH, f"//li[text()='{option_text}']")
        option = self.driver.find_element(*option_locator)
        option.click()

    def click_clear_plate_option(self):
        self.find(self.clear_plate_button).click()

    def enter_analysis_template_name(self, analysis_templates_name):
        self.type_text(self.analysis_templates_name_field, analysis_templates_name)

    def get_analysis_template_name_text(self):
        return wait_for_element(self.driver, self.REVIEW_PAGE_TITLE).text

    def clear_standard_dilution_factor(self):
        input_field = self.driver.find_element(*self.STANDARD_DILUTION_FACTOR_INPUT)

        current_value = input_field.get_attribute('value')
        for _ in range(len(current_value)):
            input_field.send_keys(Keys.BACKSPACE)

    def get_error_message_text(self):
        error_message = self.driver.find_element(*self.error_message_under_standard_dilution_page)
        return error_message.text

    def get_first_analysis_template_name(self):
        return self.wait_for(self.first_analysis_template_name_locator).text

    def click_delete_button(self):
        self.click(self.delete_button_locator)

    def is_analysis_template_present(self, scan_name):
        xpath = f"//table[@aria-label='Analysis Template']//td[contains(text(), '{scan_name}')]"
        return self.is_element_present((By.XPATH, xpath))

    def type_text_in_input_field(self, text):
        input_field = self.wait_for(self.input_field_after_save)
        input_field.send_keys(text)

    def get_input_field_value_after_save(self):
        input_field_after_save = self.wait_for(self.input_field_after_save)
        input_field_value = input_field_after_save.get_attribute('value')
        print("Actual Input Field Value After Save:", input_field_value)
        return input_field_value

    def click_save_well_button(self):
        save_button = self.wait_for(self.save_button_under_edit_well)
        save_button.click()

    def perform_right_click_and_select_option_on_row(self, option):
        alphanumeric_element = self.driver.find_element(*self.wall_point_a_locator)
        action_chains = ActionChains(self.driver)
        action_chains.context_click(alphanumeric_element).perform()
        self.driver.implicitly_wait(5)
        self.select_context_menu_option(option)

    def get_fill_attribute(self, row, column):
        well_locator = (By.XPATH, f"//div[@row='{row}' and @column='{column}']//*[name()='svg']/*[name()='path'][2]")
        fill_attribute = self.wait_for(well_locator).get_attribute('fill')
        return fill_attribute

    def verify_fill_attribute_for_wells(self, start_row, end_row, start_column, end_column, expected_fill_attribute):
        for row_number in range(start_row, end_row + 1):
            row_label = chr(ord('A') + row_number - 1)
            for column_number in range(start_column, end_column + 1):
                fill_attribute = self.get_fill_attribute(row_label, column_number)

                print(f"Fill attribute for well at Row {row_label}, Column {column_number}: {fill_attribute}")

                assert fill_attribute == expected_fill_attribute, f"Fill attribute for well at Row {row_label}, Column {column_number} is not as expected"
