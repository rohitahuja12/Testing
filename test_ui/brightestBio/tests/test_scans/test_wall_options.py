import os
import time
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.conftest import browser_driver
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.login_page import TestLoginPage


class TestScanCases:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_select_well_point_option(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_valid_barcode("WP234501")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. Verified user able to select points in well.")
        rows_columns_to_check = [("A", "5"), ("A", "12"), ("C", "4"), ("C", "8")]

        for row, column in rows_columns_to_check:
            scans_page.select_well_option(row, column)
            time.sleep(5)
            is_well_selected = scans_page.verify_well_option_selected(row, column)
            assert is_well_selected, f"Well at Row {row}, Column {column} is not selected"

    def test_select_well_option_with_shift_key(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_valid_barcode("WP234501")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. Verified user able to select points in well with swift key.")
        rows_columns_to_check = [("A", "5"), ("A", "12"), ("C", "4"), ("C", "8")]

        for row, column in rows_columns_to_check:
            scans_page.select_well_option_with_shift(row, column)
            time.sleep(5)
            is_well_selected = scans_page.verify_well_option_selected(row, column)
            assert is_well_selected, f"Well at Row {row}, Column {column} is not selected"

    def test_select_all_button_under_scan_module(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter a valid barcode.")
        scans_page.enter_valid_barcode("WP234501")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. click on Select ALl option.")
        scans_page.click_select_all_button()
        record_property("testrail_result_comment", "8. Verified all point selected in the well.")
        assert scans_page.all_wall_point_selected()
