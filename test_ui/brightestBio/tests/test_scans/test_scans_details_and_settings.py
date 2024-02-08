# import os
# import pytest
# from selenium.webdriver.remote.webdriver import WebDriver
# from brightestBio.conftest import browser_driver
# from brightestBio.pages.Scans.scan_page import ScansPage
# from brightestBio.pages.login_page import TestLoginPage
#
#
# class TestScanDetailsAndSettings:
#     @pytest.fixture(scope="function")
#     def setup(self, browser_driver: WebDriver, record_property):
#         username = os.getenv('BB_USERNAME')
#         password = os.getenv('BB_PASSWORD')
#         login_page = TestLoginPage(browser_driver)
#         login_page.login_into_application(username, password)
#         record_property("testrail_result_comment", "1. Logged in into application.")
#
#     def test_view_scan_details(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Scans module.")
#         scans_page.click_view_scan_option()
#         assert scans_page.is_date_column_visible()
#         record_property("testrail_result_comment", "3. check Date column is visible.")
#         assert scans_page.is_status_column_visible()
#         record_property("testrail_result_comment", "4. check Status column is visible.")
#         assert scans_page.is_id_column_visible()
#         record_property("testrail_result_comment", "5. check ID column is visible.")
#         assert scans_page.is_name_column_visible()
#         record_property("testrail_result_comment", "6. check Name column is visible.")
#
#     def test_scan_settings(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Scans module.")
#         scans_page.click_view_scan_option()
#         record_property("testrail_result_comment", "3. Click on Setting icon.")
#         scans_page.click_on_settings_button()
#         record_property("testrail_result_comment", "4. Uncheck ID checkbox under setting.")
#         scans_page.click_on_id_checkbox()
#         record_property("testrail_result_comment", "5. Refresh the Page.")
#         browser_driver.refresh()
#         assert not scans_page.is_id_displayed()
#         record_property("testrail_result_comment", "6. Verify ID column doesn't exist.")
#
#     def test_settings_icon_visibility_under_scans(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Scans_Page module.")
#         scans_page.click_view_scan_option()
#         record_property("testrail_result_comment", "3. check setting icon visibility ")
#         assert scans_page.is_element_present(scans_page.scan_settings_button), "Settings icon are not visible."
#
#     def test_default_view_displays_scans(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Scans_Page module.")
#         scans_page.click_view_scan_option()
#         record_property("testrail_result_comment", "6. Verify Scans details visible")
#         assert scans_page.is_default_view_displaying_scans(), "Default view does not display a list of existing scans."
