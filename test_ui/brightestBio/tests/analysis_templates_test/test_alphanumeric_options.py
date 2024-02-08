# import os
# import time
# import pytest
# from selenium.webdriver.remote.webdriver import WebDriver
# from brightestBio.pages.login_page import TestLoginPage
# from brightestBio.pages.Scans.scan_page import ScansPage
# from brightestBio.pages.analysis_templates_Page.analysis_templates import AnalysisTemplatesPage
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
#     def test_verify_svg_fill_attribute_after_click_on_make_standard(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Standard' action")
#         analysis_templates.perform_right_click_and_select_option("Make Standard")
#         record_property("testrail_result_comment", "7. Verify SVG fill attribute after 'Make Standard' action")
#         fill_attribute = analysis_templates.get_svg_fill_attribute()
#         expected_fill = "#4FC64D"
#         assert fill_attribute == expected_fill, f"Fill attribute is not {expected_fill}"
#
#     def test_verify_svg_fill_attribute_after_click_on_make_unknown(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Unknown' action")
#         analysis_templates.perform_right_click_and_select_option("Make Unknown")
#         record_property("testrail_result_comment", "7. Verify SVG fill attribute after 'Make Unknown' action")
#         fill_attribute = analysis_templates.get_svg_fill_attribute()
#         expected_fill = "#dcce54"
#         assert fill_attribute == expected_fill, f"Fill attribute is not {expected_fill}"
#
#     def test_verify_svg_fill_attribute_after_click_on_make_empty(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Empty' action")
#         analysis_templates.perform_right_click_and_select_option("Make Empty")
#         record_property("testrail_result_comment", "7. Verify SVG fill attribute after 'Make Empty' action")
#         fill_attribute = analysis_templates.get_svg_fill_attribute()
#         expected_fill = "#FFFFFF"
#         assert fill_attribute == expected_fill, f"Fill attribute is not {expected_fill}"
#
#     def test_verify_svg_fill_attribute_after_make_blank(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Blank' action")
#         analysis_templates.perform_right_click_and_select_option("Make Blank")
#         record_property("testrail_result_comment", "7. Verify SVG fill attribute after 'Make Blank' action")
#         fill_attribute = analysis_templates.get_svg_fill_attribute()
#         expected_fill = "#808080"
#         assert fill_attribute == expected_fill, f"Fill attribute is not {expected_fill}"
#
#     def test_clear_plate_chart(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#         record_property("testrail_result_comment", "7. select analysis templates platemap dropdown.")
#         plate_map_option = 'hor-2x2'
#         analysis_templates.select_plate_map_option()
#         analysis_templates.click_plate_map_option(plate_map_option)
#         time.sleep(5)
#         analysis_templates.click_clear_plate_option()
#         record_property("testrail_result_comment", "7. Verify SVG fill attribute after 'Make Blank' action")
#         fill_attribute = analysis_templates.get_svg_fill_attribute()
#         expected_fill = "#FFFFFF"
#         assert fill_attribute == expected_fill, f"Fill attribute is not {expected_fill}"
#
#     def test_verify_value_after_edit_wall_option(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#         time.sleep(4)
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#         time.sleep(5)
#         record_property("testrail_result_comment", "6. Perform 'Edit Well' action")
#         analysis_templates.perform_right_click_and_select_option("Edit Well")
#         time.sleep(5)
#         test = "a1b2"
#         analysis_templates.type_text_in_input_field(test)
#         time.sleep(5)
#         analysis_templates.click_save_well_button()
#         time.sleep(5)
#         input_field_value_after_save = analysis_templates.get_input_field_value_after_save()
#         print("Expected Input Field Value After Save: a1b2")
#         assert input_field_value_after_save == "a1b2", "Input field value after save is not as expected"
#
#     def test_verify_fill_attribute_after_mark_standard_on_row_a(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Standard' action on row a")
#         analysis_templates.perform_right_click_and_select_option_on_row('Make Standard')
#         expected_fill_attribute = "#4FC64D"
#         row_start, row_end = 1, 1
#         column_start, column_end = 1, 11
#         analysis_templates.verify_fill_attribute_for_wells(row_start, row_end, column_start, column_end,
#                                                            expected_fill_attribute)
#
#     def test_verify_fill_attribute_after_make_unknown_on_row_a(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Unknown' action on row a")
#         analysis_templates.perform_right_click_and_select_option_on_row('Make Unknown')
#         expected_fill_attribute = "#dcce54"
#         row_start, row_end = 1, 1
#         column_start, column_end = 1, 11
#         analysis_templates.verify_fill_attribute_for_wells(row_start, row_end, column_start, column_end,
#                                                            expected_fill_attribute)
#
#     def test_verify_fill_attribute_after_make_blank_on_row_a(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Blank' action on row a")
#         analysis_templates.perform_right_click_and_select_option_on_row('Make Blank')
#         expected_fill_attribute = "#808080"
#         row_start, row_end = 1, 1
#         column_start, column_end = 1, 11
#         analysis_templates.verify_fill_attribute_for_wells(row_start, row_end, column_start, column_end,
#                                                            expected_fill_attribute)
#
#     def test_verify_fill_attribute_after_make_empty_on_row_a(self, browser_driver, record_property, setup):
#         scans_page = ScansPage(browser_driver)
#         analysis_templates = AnalysisTemplatesPage(browser_driver)
#         record_property("testrail_result_comment", "2. Navigate to the Analysis templates module.")
#         analysis_templates.click_view_analysis_templates_option()
#
#         record_property("testrail_result_comment", "3. Initiate Analysis template Creation.")
#         analysis_templates.click_on_create_now_button()
#
#         record_property("testrail_result_comment", "4. Choose a template type (e.g., 96-well-plate).")
#         analysis_templates.get_product_card(0)
#
#         record_property("testrail_result_comment", "5. User click on next button")
#         scans_page.click_on_next_button()
#
#         record_property("testrail_result_comment", "6. Perform 'Make Empty' action on row a")
#         analysis_templates.perform_right_click_and_select_option_on_row('Make Empty')
#         expected_fill_attribute = "#FFFFFF"
#         row_start, row_end = 1, 1
#         column_start, column_end = 1, 11
#         analysis_templates.verify_fill_attribute_for_wells(row_start, row_end, column_start, column_end,
#                                                            expected_fill_attribute)
