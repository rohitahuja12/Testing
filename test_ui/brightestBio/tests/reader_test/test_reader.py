import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.login_page import TestLoginPage
from brightestBio.pages.reader_Page.reader_page import ReaderPage


class TestReader:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_check_reader_title_visibility(self, browser_driver: WebDriver, record_property, setup):
        reader = ReaderPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Reader module.")
        reader.click_view_on_reader_option()
        time.sleep(2)
        record_property("testrail_result_comment", "3. Check if the default title of the reader is visible.")
        actual_title = reader.get_reader_title_text()
        record_property("testrail_result_comment", "4. Verified default title of the reader is visible.")
        expected_title = "Readers"
        assert actual_title == expected_title, f"Expected title: '{expected_title}', but got: '{actual_title}'"

    def test_go_back_to_dashboard_from_reader_page(self, browser_driver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        login_page = TestLoginPage(browser_driver)

        reader = ReaderPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Reader feature.")
        reader.click_view_on_reader_option()
        scans_page.click_back_to_dashboard_button()
        record_property("testrail_result_comment", "3. Click on 'back to dashboard' button.")
        time.sleep(5)
        empower_dashboard = browser_driver.find_element(By.XPATH, login_page.empowerDashboard)
        assert empower_dashboard.is_displayed()
        record_property("testrail_result_comment", "4. Verified User is successfully back to dashboard")

    def test_default_view_displays_reader(self, browser_driver: WebDriver, record_property, setup):
        reader = ReaderPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Reader feature.")
        reader.click_view_on_reader_option()
        record_property("testrail_result_comment", "3. Verified default reader details visible")
        assert reader.is_default_view_displaying_reader(), "Default view does not display a list of existing reader."

    def test_view_reader_options_details(self, browser_driver: WebDriver, record_property, setup):
        reader = ReaderPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Reader feature.")
        reader.click_view_on_reader_option()
        time.sleep(1)
        record_property("testrail_result_comment", "3.verified Door column is visible.")
        assert reader.is_door_column_visible_under_reader_module()
        record_property("testrail_result_comment", "4. verified Serial Number column is visible.")
        assert reader.is_serial_number_column_visible_under_reader_module()
