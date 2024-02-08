# import os
# import time
# import pytest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.remote.webdriver import WebDriver
# from brightestBio.pages.Scans.scan_page import ScansPage
# from brightestBio.pages.analysis_templates_Page.analysis_templates import AnalysisTemplatesPage
# from brightestBio.pages.login_page import TestLoginPage
#
#
# class TestAnalysisTemplates:
#     @pytest.fixture(scope="function")
#     def setup(self, browser_driver: WebDriver, record_property):
#         username = os.getenv('BB_USERNAME')
#         password = os.getenv('BB_PASSWORD')
#         login_page = TestLoginPage(browser_driver)
#         login_page.login_into_application(username, password)
#         record_property("testrail_result_comment", "1. Logged in into application.")
#
#     def test_check_analysis_templates_title_visibility(self, browser_driver: WebDriver, record_property, setup):
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Analysis_Templates feature.")
#         analysis_templates.click_view_analysis_templates_option()
#         time.sleep(2)
#
#         record_property("testrail_result_comment",
#                         "3. Check if the default title of the Analysis_Templates is visible.")
#         actual_title = analysis_templates.get_analysis_template_title_text()
#         expected_title = "Analysis Templates"
#         assert actual_title == expected_title, f"Expected title: '{expected_title}', but got: '{actual_title}'"
#
#     def test_view_analysis_templates_details(self, browser_driver: WebDriver, record_property, setup):
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2.Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#         time.sleep(2)
#         assert scans_page.is_date_column_visible()
#         record_property("testrail_result_comment", "3.Date column is visible under Analysis template.")
#         assert analysis_templates.is_product_column_visible_under_analysis_template_module()
#         record_property("testrail_result_comment", "4. Product column is visible under Analysis template.")
#         assert analysis_templates.is_product_column_visible_under_analysis_template_module()
#         record_property("testrail_result_comment", "5. Protocol column is visible under Analysis template.")
#         assert scans_page.is_name_column_visible()
#         record_property("testrail_result_comment", "6. Name column is visible under Analysis template.")
#
#     def test_settings_options_visibility_under_analysis_template(self, browser_driver: WebDriver, record_property,
#                                                                  setup):
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         scans_page = ScansPage(browser_driver)
#
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#         record_property("testrail_result_comment", "3. Verified Setting Icon visible")
#         assert scans_page.is_element_present(scans_page.scan_settings_button), "Settings options are not visible."
#
#     def test_analysis_templates_settings_options(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#         record_property("testrail_result_comment", "3. Click on Setting icon")
#         scans_page.click_on_settings_button()
#         record_property("testrail_result_comment", "4. UnCheck Protocol check box under setting options")
#         analysis_templates.click_on_protocol_checkbox_under_setting_icon()
#         record_property("testrail_result_comment", "5. Refresh the Page")
#         browser_driver.refresh()
#         record_property("testrail_result_comment", "6. Verify Protocol column doesn't exist")
#         assert not analysis_templates.is_protocol_column_visible__analysis_template_module()
#
#     def test_default_view_displays_analysis_templates(self, browser_driver: WebDriver, record_property, setup):
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#         record_property("testrail_result_comment", "3. Verify Analysis templates details visible")
#         assert analysis_templates.is_default_view_displaying_analysis_templates(), "Default view does not display a list of existing Analysis."
#
#     def test_verify_product_availability_under_analysis_templates(self, browser_driver: WebDriver, record_property,
#                                                                   setup):
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#
#         product_cards = analysis_templates.get_product_cards()
#         print(f"Number of products available: {len(product_cards)}")
#
#         assert len(product_cards) > 0, "No products available on the Analyses Templates page."
#
#     def test_blank_analysis_templates_name_field(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "2. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "3. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(3)
#         time.sleep(5)
#         record_property("testrail_result_comment", "4. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "5. do not enter analysis templates name.")
#         analysis_templates.enter_analysis_template_name("")
#         record_property("testrail_result_comment", "6. Verified 'Next' button should not be enabled.")
#         assert not scans_page.next_button_enabled()
#
#     def test_verify_analysis_template_name_visible_in_review_page(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#         time.sleep(5)
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "6. Enter analysis templates name.")
#         random_analysis_templates_name = analysis_templates.generate_random_name()
#         analysis_templates.enter_analysis_template_name(random_analysis_templates_name)
#         record_property("testrail_result_comment", "7. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "8. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "9. Verified entered name visible in review page")
#         review_page_title = analysis_templates.get_analysis_template_name_text()
#         assert review_page_title == random_analysis_templates_name, f"Expected '{random_analysis_templates_name}', but got '{review_page_title}'."
#
#     def test_error_message_and_disabled_next_button_on_missing_standard_concentrations(self, browser_driver,
#                                                                                        record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#         time.sleep(5)
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "6. Enter analysis templates name.")
#         random_analysis_templates_name = analysis_templates.generate_random_name()
#         analysis_templates.enter_analysis_template_name(random_analysis_templates_name)
#         record_property("testrail_result_comment", "7. select analysis templates platemap dropdown.")
#         plate_map_option = 'hor-2x2'
#         analysis_templates.select_plate_map_option()
#         analysis_templates.click_plate_map_option(plate_map_option)
#         record_property("testrail_result_comment", "8. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "9. Clear 'standard dilution' and verify the error")
#         analysis_templates.clear_standard_dilution_factor()
#         actual_error_message = analysis_templates.get_error_message_text()
#         expected_error_message = "Please enter a valid dilution factor."
#         assert actual_error_message == expected_error_message, f"Expected: {expected_error_message}, Actual: {actual_error_message}"
#
#     def test_go_back_to_dashboard_from_analysis_template_page(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         login_page = TestLoginPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#         scans_page.click_back_to_dashboard_button()
#         record_property("testrail_result_comment", "3. Click on 'back to dashboard' option.")
#         time.sleep(5)
#         empower_dashboard = browser_driver.find_element(By.XPATH, login_page.empowerDashboard)
#         assert empower_dashboard.is_displayed()
#         record_property("testrail_result_comment", "4. Verified User is successfully back to dashboard")
