import os
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.pages.documents_Page.document_page import DocumentPage
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.login_page import TestLoginPage


class TestDocuments:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_check_documents_title_visibility(self, browser_driver: WebDriver, record_property, setup):
        document = DocumentPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Reader module.")
        document.click_view_on_documents_option()
        time.sleep(2)
        record_property("testrail_result_comment", "3. Check if the default title of the reader is visible.")
        actual_title = document.get_document_title_text()
        record_property("testrail_result_comment", "4. Verified default title of the reader is visible.")
        expected_title = "Documentss"
        assert actual_title == expected_title, f"Expected title: '{expected_title}', but got: '{actual_title}'"

    def test_go_back_to_dashboard_from_documents_page(self, browser_driver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        login_page = TestLoginPage(browser_driver)

        document = DocumentPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Documents module.")
        document.click_view_on_documents_option()
        scans_page.click_back_to_dashboard_button()
        record_property("testrail_result_comment", "3. Click on back to dashboard button.")
        time.sleep(5)
        empower_dashboard = browser_driver.find_element(By.XPATH, login_page.empowerDashboard)
        assert empower_dashboard.is_displayed()
        record_property("testrail_result_comment", "4. Verified User is successfully back to dashboard")
#
#     def test_verify_connect_to_empower_reader_document(self, browser_driver, record_property, setup):
#         document_page = DocumentPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Documents module.")
#         document_page.click_view_on_documents_option()
#         assert document_page.verify_document_availability("Connnect to the Empower Reader")
#
#     def test_verify_load_a_plate_document(self, browser_driver, record_property, setup):
#         document_page = DocumentPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Documents module.")
#         document_page.click_view_on_documents_option()
#         assert document_page.verify_document_availability("Load a plate")
#
#     def test_verify_product_kit_document(self, browser_driver, record_property, setup):
#         document_page = DocumentPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Documents module.")
#         document_page.click_view_on_documents_option()
#         assert document_page.verify_document_availability("Product Kit")
#
#     def test_sign_out_button_visibility_under_documents(self, browser_driver, record_property, setup):
#         document_page = DocumentPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Documents module.")
#         document_page.click_view_on_documents_option()
#         assert document_page.is_sign_out_button_visible(), "Sign Out button is not visible"
#
#     def test_profile_icon_visibility_under_documents(self, browser_driver, record_property, setup):
#         document_page = DocumentPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Documents module.")
#         document_page.click_view_on_documents_option()
#         assert document_page.is_profile_icon_visible(), "Profile icon is not visible"
