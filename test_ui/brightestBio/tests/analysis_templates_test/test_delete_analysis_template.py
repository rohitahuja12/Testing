# import os
# import pytest
# from selenium.webdriver.remote.webdriver import WebDriver
# from brightestBio.pages.analysis_templates_Page.analysis_templates import AnalysisTemplatesPage
# from brightestBio.pages.login_page import TestLoginPage
#
#
# class TestLoginApplication:
#     @pytest.fixture(scope="function")
#     def setup(self, browser_driver: WebDriver, record_property):
#         username = os.getenv('BB_USERNAME')
#         password = os.getenv('BB_PASSWORD')
#         login_page = TestLoginPage(browser_driver)
#         login_page.login_into_application(username, password)
#         record_property("testrail_result_comment", "1. Logged in into application.")
#
#     class TestAnalysisTemplateDeletion:
#         @staticmethod
#         def test_delete_analysis_template(browser_driver: WebDriver, record_property, setup):
#             analysis_templates = AnalysisTemplatesPage(browser_driver)
#             record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#             analysis_templates.click_view_analysis_templates_option()
#
#             record_property("testrail_result_comment", "3.Get the name of the first scan.")
#             analysis_template = analysis_templates.get_first_analysis_template_name()
#             print(analysis_templates)
#
#             record_property("testrail_result_comment", "4.delete first created analysis template.")
#             analysis_templates.click_delete_button()
#
#             record_property("testrail_result_comment", "5.Verify that the deleted analysis template is not present.")
#             assert not analysis_templates.is_analysis_template_present(analysis_template), f"Analysis '{analysis_template}' is still present after deletion."
