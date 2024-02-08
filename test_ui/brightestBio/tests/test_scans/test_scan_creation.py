import os
import time
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.conftest import browser_driver
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.login_page import TestLoginPage


class TestScanCreation:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_v_3_scan_creation_flow(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter valid barcode and click on 'Next' button.")
        scans_page.enter_valid_barcode("WP234501")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. On the Scan Details page, select 'Select All' option.")
        scans_page.click_select_all_button()

        record_property("testrail_result_comment", "8. Click on next button.")
        scans_page.click_on_next_button()

        record_property("testrail_result_comment", "9. Click on 'Create' Button under review page.")
        scans_page.click_on_create_under_review_page()
        time.sleep(3)

        record_property("testrail_result_comment", "10. Verify the scan is created.")
        created_scan_name = scans_page.get_created_scan_name()
        assert created_scan_name == random_scan_name

    def test_delete_scan(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2.Go to View Scan tab.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "1.Get the name of the first scan.")
        scan_name = scans_page.get_first_scan_name()
        print(scan_name)
        #
        record_property("testrail_result_comment", "3.delete first created scan.")
        scans_page.click_delete_button()
        time.sleep(2)

        record_property("testrail_result_comment", "4.Verify that the deleted scan is not present.")
        assert not scans_page.is_scan_present(scan_name), f"Scan '{scan_name}' is still present after deletion."

    def test_v_2_scan_creation_flow(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Scans_Page feature.")
        scans_page.click_view_scan_option()

        record_property("testrail_result_comment", "3. Initiate Scan Creation.")
        scans_page.initiate_scan_creation()
        time.sleep(3)

        record_property("testrail_result_comment", "4. Enter valid barcode and click on 'Next'.")
        scans_page.enter_valid_barcode("WP230622")

        record_property("testrail_result_comment", "5. Enter scan name.")
        random_scan_name = scans_page.generate_random_scan_name()
        scans_page.enter_scan_name(random_scan_name)

        record_property("testrail_result_comment", "6. Select a value from the reader dropdown.")
        scans_page.select_reader()

        record_property("testrail_result_comment", "7. On the Scan Details page, select 'Select All' option.")
        scans_page.click_select_all_button()

        record_property("testrail_result_comment", "8. Click on next button.")
        scans_page.click_on_next_button()

        record_property("testrail_result_comment", "9. Click on 'Create' Button under review page.")
        scans_page.click_on_create_under_review_page()
        time.sleep(3)

        record_property("testrail_result_comment", "10. Verify the created scan name.")
        created_scan_name = scans_page.get_created_scan_name()
        assert created_scan_name == random_scan_name

    def test_delete_v2_scan(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2.Go to View Scan tab.")
        scans_page.click_view_scan_option()
        #
        record_property("testrail_result_comment", "1.Get the name of the first scan.")
        scan_name = scans_page.get_first_scan_name()
        print(scan_name)
        #
        record_property("testrail_result_comment", "3.delete first created scan.")
        scans_page.click_delete_button()
        time.sleep(2)

        record_property("testrail_result_comment", "4.Verify that the deleted scan is not present.")
        assert not scans_page.is_scan_present(scan_name), f"Scan '{scan_name}' is still present after deletion."
