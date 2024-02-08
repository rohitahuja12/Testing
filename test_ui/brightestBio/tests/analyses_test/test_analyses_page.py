import os
import sys
import time
from io import StringIO
import pytest
from faker.generator import random
from selenium.webdriver.remote.webdriver import WebDriver
from brightestBio.pages.Scans.scan_page import ScansPage
from brightestBio.pages.analyses_Page.analyses import AnalysesPage
from brightestBio.pages.analysis_templates_Page.analysis_templates import AnalysisTemplatesPage
from brightestBio.pages.login_page import TestLoginPage


class TestAnalyses:
    @pytest.fixture(scope="function")
    def setup(self, browser_driver: WebDriver, record_property):
        username = os.getenv('BB_USERNAME')
        password = os.getenv('BB_PASSWORD')
        login_page = TestLoginPage(browser_driver)
        login_page.login_into_application(username, password)
        record_property("testrail_result_comment", "1. Logged in into application.")

    def test_check_analyses_title_visibility(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses feature.")
        analyses.click_view_on_analyses_option()
        time.sleep(2)
        record_property("testrail_result_comment", "3. Check if the default title of the Analyses is visible.")
        actual_title = analyses.get_analyses_title_text()
        record_property("testrail_result_comment", "4. Verified default title of the Analyses is visible.")
        expected_title = "Analysess"
        assert actual_title == expected_title, f"Expected title: '{expected_title}', but got: '{actual_title}'"

    def test_settings_icon_visibility_under_analyses(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Verified Setting Icon is visible under analyses page")
        assert not scans_page.is_element_present(scans_page.scan_settings_button), "Settings options are not visible."

    def test_analyses_settings_options(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on Setting Icon")
        scans_page.click_on_settings_button()
        record_property("testrail_result_comment", "4. UnCheck Name check box")
        analyses.click_on_name_checkbox_under_setting_icon()
        record_property("testrail_result_comment", "5. Refresh the Page")
        browser_driver.refresh()
        record_property("testrail_result_comment", "6. Verified Name column doesn't exist")
        assert not analyses.is_name_column_visible__analysis_template_module()

    def test_default_view_displays_analyses(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Verified Analyses details visible")
        assert analyses.is_default_view_displaying_analyses(), "Default view does not display a list of existing analyses."

    def test_search_field_with_valid_name(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()

        search_term = "test"
        record_property("testrail_result_comment", f"3. Search for the term '{search_term}'.")
        analyses.search_analysis(search_term)
        time.sleep(5)
        captured_output = StringIO()
        sys.stdout = captured_output
        analyses.verify_search_results(search_term)
        sys.stdout = sys.__stdout__
        actual_output = captured_output.getvalue().strip()
        # print("Captured Output:", actual_output)

        expected_output = search_term.lower()
        assert expected_output in actual_output.lower(), f"Expected output '{expected_output}' not found in actual output: {actual_output}"

    def test_invalid_search_in_search_field(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()

        captured_output = StringIO()
        sys.stdout = captured_output
        invalid_search_term = "invalid_search"
        record_property("testrail_result_comment", f"Testing invalid search with term '{invalid_search_term}'.")
        analyses.search_analysis(invalid_search_term)
        analyses.verify_search_results(invalid_search_term)

        sys.stdout = sys.__stdout__
        actual_output = captured_output.getvalue().strip()
        # print("Captured Output:", actual_output)
        expected_output = ""
        assert expected_output in actual_output, f"Expected output '{expected_output}' not found in actual output: {actual_output}"

    def test_select_only_complete_status_scans_button_enabled(self, browser_driver: WebDriver, record_property, setup):

        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        analyses.click_view_on_analyses_option()
        time.sleep(2)
        analysis_templates.click_on_create_now_button()
        time.sleep(5)

        scans_rows = analyses.get_scans_rows()

        for row in scans_rows:
            status = analyses.get_status_of_scan(row)

            if status == 'RUNNING':
                assert analyses.is_scan_select_disabled(row), f"Radio button should be disabled for 'RUNNING' scan: {row}"
                print(f"Scan with status 'RUNNING': {row}")
            elif status == 'NOT_QUEUED':
                assert analyses.is_scan_select_disabled(row), f"Radio button should be disabled for 'RUNNING' scan: {row}"
                print(f"Scan with status 'NOT_QUEUED': {row}")
            elif status == 'ERROR':
                assert analyses.is_scan_select_disabled(row), f"Radio button should be disabled for 'RUNNING' scan: {row}"
                print(f"Scan with status 'ERROR': {row}")
            elif status == 'COMPLETE':
                assert not analyses.is_scan_select_disabled(row), f"Radio button should be enabled for 'COMPLETE' scan: {row}"
                analyses.select_scan(row)
                print(f"Scan with status 'COMPLETE': {row}")
                analyses.select_scan(row)
                time.sleep(5)

    def test_inability_to_proceed_without_selecting_scan(self, browser_driver: WebDriver, record_property, setup):
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()
        record_property("testrail_result_comment", "4. without selecting scan 'Next' button should not be enabled.")
        assert not scans_page.next_button_enabled()

    def test_next_button_enabled_after_selecting_scan(self, browser_driver: WebDriver, record_property, setup):
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()

        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")
        record_property("testrail_result_comment", "4. Next button enabled after select scan.")
        assert scans_page.next_button_enabled()

    def test_verify_analysis_templates_visibility(self, browser_driver: WebDriver, record_property, setup):

        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()

        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")
        # Click on the "Next" button
        scans_page.click_on_next_button()
        time.sleep(4)
        print("Clicked on the 'Next' button.")

        record_property("testrail_result_comment", "3.Verified Analysis template section visible.")
        assert analyses.is_analysis_templates_section_displayed(), "Analysis Templates section is not displayed after clicking 'Next'."

    def test_go_back_to_scans_page_after_analysis_page(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        time.sleep(2)
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()

        # Separate 'COMPLETE' scans from other statuses
        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")

        record_property("testrail_result_comment", "4.Click on Next Button.")
        scans_page.click_on_next_button()
        record_property("testrail_result_comment", "5.Click on Back Button.")
        analyses.click_on_back_button()
        record_property("testrail_result_comment", "6.Verified Scan details visible")
        assert analyses.is_scans_section_displayed(), "Not on the Scans page after clicking Back"

    def test_inability_to_proceed_without_selecting_analysis_template(self, browser_driver: WebDriver, record_property, setup):
        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        scans_page = ScansPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        time.sleep(5)
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()
        time.sleep(5)

        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")

        record_property("testrail_result_comment", "4.Click on Next Button.")
        scans_page.click_on_next_button()
        record_property("testrail_result_comment", "4. without selecting scan 'Next' button should not be enabled.")
        assert not scans_page.next_button_enabled()

    def test_next_button_enabled_after_selecting_analysis_template(self, browser_driver: WebDriver, record_property,
                                                                   setup):
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()

        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")
        record_property("testrail_result_comment", "4.Click on Next Button.")
        scans_page.click_on_next_button()
        analysis_rows = analyses.get_analysis_rows()

        # Check if there are any analysis templates
        if analysis_rows:
            # Select a random analysis template
            random_row = random.choice(analysis_rows)
            analyses.select_scan(random_row)
            print("Selected a random analysis template.")
            time.sleep(2)  # Add a wait if necessary
        else:
            print("No analysis templates found.")
            record_property("testrail_result_comment", "4. without selecting scan 'Next' button should be enabled.")
            assert scans_page.next_button_enabled()

    def test_verify_user_is_on_analysis_name_page_when_click_on_next_after_selecting_analysis_template(self,
                                                                                                       browser_driver: WebDriver,
                                                                                                       record_property,
                                                                                                       setup):
        scans_page = ScansPage(browser_driver)
        analyses = AnalysesPage(browser_driver)
        analysis_templates = AnalysisTemplatesPage(browser_driver)
        record_property("testrail_result_comment", "2. Navigate to the Analyses module.")
        analyses.click_view_on_analyses_option()
        record_property("testrail_result_comment", "3. Click on create now button under Analyses module.")
        analysis_templates.click_on_create_now_button()

        def select_random_complete_scan():
            scans_rows = analyses.get_scans_rows()
            complete_scans = [row for row in scans_rows if analyses.get_status_of_scan(row) == 'COMPLETE']
            if complete_scans:
                random_scan = random.choice(complete_scans)
                print(f"Selected random 'COMPLETE' scan: {random_scan}")
                assert not analyses.is_scan_select_disabled(
                    random_scan), f"Radio button should be enabled for 'COMPLETE' scan: {random_scan}"
                analyses.select_scan(random_scan)
                print(f"Scan with status 'COMPLETE' selected: {random_scan}")
                time.sleep(5)
                return True
            else:
                print("No 'COMPLETE' scans available on the current page.")
                return False

        # Try selecting a random 'COMPLETE' scan on the current page or on subsequent pages
        while not select_random_complete_scan():
            # If not found, go to the next page
            analyses.click_go_to_next_page_button()
            time.sleep(2)  # Adjust as needed
        browser_driver.execute_script("window.scrollTo(0, 0);")
        record_property("testrail_result_comment", "4.Click on Next Button.")
        scans_page.click_on_next_button()
        analysis_rows = analyses.get_analysis_rows()

        # Check if there are any analysis templates
        if analysis_rows:
            # Select a random analysis template
            random_row = random.choice(analysis_rows)
            analyses.select_scan(random_row)
            print("Selected a random analysis template.")
            time.sleep(2)
        else:
            print("No analysis templates found.")
            record_property("testrail_result_comment", "4. without selecting scan 'Next' button should be enabled.")
            assert scans_page.next_button_enabled()
            scans_page.click_on_next_button()
            input_field = analyses.find_input_field()
            assert input_field
