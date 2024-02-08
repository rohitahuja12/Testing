# import os
# import pytest
# from selenium.webdriver.remote.webdriver import WebDriver
# from brightestBio.conftest import browser_driver
# from brightestBio.pages.Dashboard_Page.dashboard import DashboardPage
# from brightestBio.pages.login_page import TestLoginPage
#
#
# class TestDashboardPage:
#     @pytest.fixture(scope="function")
#     def setup(self, browser_driver: WebDriver, record_property):
#         username = os.getenv('BB_USERNAME')
#         password = os.getenv('BB_PASSWORD')
#         login_page = TestLoginPage(browser_driver)
#         login_page.login_into_application(username, password)
#         record_property("testrail_result_comment", "1. Logged in into application.")
#
#     def test_check_elements_visibility(self, browser_driver: WebDriver, record_property, setup):
#         dashboard_page = DashboardPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the dashboard page.")
#
#         record_property("testrail_result_comment", "3. Check if the 'Scans' element is visible.")
#         assert dashboard_page.is_scan_name_visible(), "'Scans' element is not visible on the dashboard."
#
#         record_property("testrail_result_comment", "4. Check if the 'Analysis Templates' element is visible.")
#         assert dashboard_page.is_analysis_templates_visible(), "Analysis Templates element is not visible on the dashboard."
#
#         record_property("testrail_result_comment", "5. Check if the 'Analyses' element is visible.")
#         assert dashboard_page.is_analyses_visible(), "Analyses' element is not visible on the dashboard."
#
#         record_property("testrail_result_comment", "6. Verified visibility of elements.")
#
#     def test_check_dashboard_title_visibility(self, browser_driver: WebDriver, record_property, setup):
#         dashboard_page = DashboardPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the dashboard page.")
#
#         record_property("testrail_result_comment", "3. Check if the default title of the dashboard is visible.")
#         assert dashboard_page.is_dashboard_title_visible(), "Default dashboard title is not visible."
#
#         record_property("testrail_result_comment", "4. Verified visibility of the default dashboard title.")
#
#     def test_check_version_number_visibility(self, browser_driver: WebDriver, record_property, setup):
#         dashboard_page = DashboardPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the dashboard page.")
#
#         record_property("testrail_result_comment", "3. Check if the version number of the dashboard is visible.")
#         assert dashboard_page.is_version_number_visible(), "Dashboard version number is not visible."
#
#         record_property("testrail_result_comment", "4. Verified visibility of the dashboard version number.")
#
#     def test_check_dashboard_title_style(self, browser_driver: WebDriver, record_property, setup):
#         dashboard_page = DashboardPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the dashboard page.")
#
#         record_property("testrail_result_comment",
#                         "3. Inspect the font style, size, and formatting of the dashboard title.")
#         font_size = dashboard_page.get_dashboard_title_style("font-size")
#         font_family = dashboard_page.get_dashboard_title_style("font-family")
#         font_weight = dashboard_page.get_dashboard_title_style("font-weight")
#         text_color = dashboard_page.get_dashboard_title_style("color")
#
#         print(f"Font Size: {font_size}")
#         print(f"Font Family: {font_family}")
#         print(f"Font Weight: {font_weight}")
#         print(f"Text Color: {text_color}")
