import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.conftest import browser_driver
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.login_page import TestLoginPage


class TestScansPage:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_next_button_not_enabled_for_blank_barcode(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)

        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. do not enter anything in the barcode field.")
        scans_page.blank_barcode()

        record_property("testrail_result_comment", "5. Expected Result: 'Next' button should not be enabled.")
        assert not scans_page.next_button_enabled()

    def test_verify_v2barcode_information_visibility(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(2)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.check_bar_code_details("WP230622")

        record_property("testrail_result_comment", "5. Verify barcode information is visible after entering a valid barcode")
        barcode_info_element = scans_page.find(scans_page.barcode_info_locator)
        assert barcode_info_element.is_displayed()
        assert barcode_info_element.text == "V2_Human_Inflammatory_Kit_12P_082323_2_universal"

    def test_verify_v3barcode_information_visibility(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(2)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.check_bar_code_details("WP234610")

        record_property("testrail_result_comment", "5. Verify barcode information is visible after entering a valid barcode")
        barcode_info_element = scans_page.find(scans_page.barcode_info_locator)
        assert barcode_info_element.is_displayed(), "Barcode information is not visible after entering a valid barcode."
        assert barcode_info_element.text == "V3_Inflammatory_Kit_12P_092923"

    def test_next_button_not_enabled_for_invalid_barcode(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)

        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. Enter an invalid barcode.")
        scans_page.enter_invalid_barcode("WP23450")

        record_property("testrail_result_comment", "5. Expected Result: 'Next' button should not be enabled.")
        assert not scans_page.next_button_enabled()

    def test_next_button_enabled_for_valid_barcode(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)

        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_invalid_barcode("WP234505")

        record_property("testrail_result_comment", "5. Expected Result: 'Next' button should be enabled.")
        assert scans_page.next_button_enabled()

    def test_blank_scan_name_next_button_not_enabled(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)

        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        time.sleep(3)
        scans_page.enter_valid_barcode("WP234505")

        record_property("testrail_result_comment", "5. Check next button not enabled.")
        assert not scans_page.next_button_enabled()

    def test_without_entering_scan_name_next_button_not_enabled(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)

        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_valid_barcode("WP234505")

        record_property("testrail_result_comment", "5. Enter Scan Name.")
        scans_page.enter_scan_name("test123")

        record_property("testrail_result_comment", "6. Check next button not enabled.")
        assert not scans_page.next_button_enabled()

    def test_next_button_enabled_after_entering_scan_details(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. Enter a valid barcode.")

        scans_page.enter_valid_barcode("WP234505")

        record_property("testrail_result_comment", "5. Enter scan name.")
        scans_page.enter_scan_name("test123")

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. Check next button enabled.")
        assert scans_page.next_button_enabled()

    def test_verify_scans_details_in_review_page(self, browser_driver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_valid_barcode("WP234501")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. On the Scan Details page, select 'Select All' option.")
        scans_page.click_select_all_button()

        record_property("testrail_result_comment", "8. click on next button.")
        scans_page.click_on_next_button()
        record_property("testrail_result_comment", "8. Verify display scan name should match with  entered scan name.")

        displayed_scan_name = scans_page.get_review_page_title()
        assert displayed_scan_name == random_scan_name, "Displayed scan name does not match entered scan name."

    def test_go_back_to_dashboard_from_scan_page(self, browser_driver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        login_page = TestLoginPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page module.")
        scans_page.click_view_scan_option()
        record_property("testrail_result_comment", "3. Click on Back To Dashboard button.")
        scans_page.click_back_to_dashboard_button()
        time.sleep(5)
        empower_dashboard = browser_driver.find_element(By.XPATH, login_page.empowerDashboard)
        assert empower_dashboard.is_displayed()
        record_property("testrail_result_comment", "4. Verified User is successfully loggedIn")
