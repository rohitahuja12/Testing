# import os
# import time
# import pytest
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
#     def test_create_new_analysis_template_with_96_well_plate_product(self, browser_driver: WebDriver, record_property,
#                                                                      setup):
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
#         record_property("testrail_result_comment", "9. User click on create button")
#         scans_page.click_on_create_under_review_page()
#         time.sleep(4)
#         record_property("testrail_result_comment", "10. Verify the created analysis template name.")
#         created_analysis_template_name = analysis_templates.get_first_analysis_template_name()
#         assert created_analysis_template_name == random_analysis_templates_name
#         print(created_analysis_template_name)
#
#     def test_create_new_analysis_template_with_v3_product(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., v3_product).")
#         analysis_templates.get_product_card(1)
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
#         record_property("testrail_result_comment", "9. User click on create button")
#         scans_page.click_on_create_under_review_page()
#         time.sleep(4)
#         record_property("testrail_result_comment", "10. Verify the created analysis template name.")
#         created_analysis_template_name = analysis_templates.get_first_analysis_template_name()
#         assert created_analysis_template_name == random_analysis_templates_name
#         record_property("testrail_result_comment", "11.Get the name of the first scan.")
#         analysis_template = analysis_templates.get_first_analysis_template_name()
#         print(analysis_templates)
#
#         record_property("testrail_result_comment", "12.delete first created analysis template.")
#         analysis_templates.click_delete_button()
#
#         record_property("testrail_result_comment", "13.Verify that the deleted analysis template is not present.")
#         assert not analysis_templates.is_analysis_template_present(analysis_template), f"Analysis '{analysis_template}' is still present after deletion."
#
#     def test_create_new_analysis_template_with_v2_product(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., v2_product).")
#         analysis_templates.get_product_card(2)
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
#         record_property("testrail_result_comment", "9. User click on create button")
#         scans_page.click_on_create_under_review_page()
#         time.sleep(4)
#         record_property("testrail_result_comment", "10. Verify the created analysis template name.")
#         created_analysis_template_name = analysis_templates.get_first_analysis_template_name()
#         assert created_analysis_template_name == random_analysis_templates_name
#         record_property("testrail_result_comment", "11.Get the name of the first analysis template.")
#         analysis_template = analysis_templates.get_first_analysis_template_name()
#         print(analysis_templates)
#
#         record_property("testrail_result_comment", "12. Delete first created analysis template.")
#         analysis_templates.click_delete_button()
#
#         record_property("testrail_result_comment", "13.Verify that the deleted analysis template is not present.")
#         assert not analysis_templates.is_analysis_template_present(analysis_template), f"Analysis '{analysis_template}' is still present after deletion."
#
#     def test_create_new_analysis_template_with_v31_product(self, browser_driver: WebDriver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(3)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., v3.1_product).")
#         analysis_templates.get_product_card(3)
#         time.sleep(5)
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "6. Enter analysis templates name.")
#         random_analysis_templates_name = analysis_templates.generate_random_name()
#         analysis_templates.enter_analysis_template_name(random_analysis_templates_name)
#         print(random_analysis_templates_name)
#         record_property("testrail_result_comment", "7. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "8. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "9. User click on create button")
#         scans_page.click_on_create_under_review_page()
#         time.sleep(10)
#         record_property("testrail_result_comment", "10. Verify the created analysis template name.")
#         created_analysis_template_name = analysis_templates.get_first_analysis_template_name()
#         assert created_analysis_template_name == random_analysis_templates_name
#         record_property("testrail_result_comment", "11.Get the name of the first analysis template.")
#         analysis_template = analysis_templates.get_first_analysis_template_name()
#         print(analysis_templates)
#
#         record_property("testrail_result_comment", "12.delete first created analysis template.")
#         analysis_templates.click_delete_button()
#
#         record_property("testrail_result_comment", "13.Verify that the deleted analysis template is not present.")
#         assert not analysis_templates.is_analysis_template_present(analysis_template), f"Analysis '{analysis_template}' is still present after deletion."
