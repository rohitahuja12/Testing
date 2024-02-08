from selenium.webdriver.common.by import By
from brightestBio.pages.common import CommonOps


class DashboardPage(CommonOps, ):
    scan_name_element = (By.XPATH, "//div[contains(text(), 'Scans')]")
    analysis_templates_element = (By.XPATH, "//div[contains(text(), 'Analysis Templates')]")
    analyses_element = (By.XPATH, "//div[contains(text(), 'Analyses')]")
    empowerDashboard = (By.XPATH, "//*[contains(text(), 'Empower Dashboard')]")
    version_number = (By.XPATH, "//span[@class='MuiChip-label MuiChip-labelMedium css-9iedg7']")
    dashboard_title = (By.XPATH, "//div[@class='MuiTypography-root MuiTypography-h5 MuiTypography-gutterBottom css-ubdxaf']")

    def is_scan_name_visible(self):
        return self.find(self.scan_name_element).is_displayed()

    def is_analysis_templates_visible(self):
        return self.find(self.analysis_templates_element).is_displayed()

    def is_analyses_visible(self):
        return self.find(self.analyses_element).is_displayed()

    def is_dashboard_title_visible(self):
        return self.find(self.empowerDashboard).is_displayed()

    def is_version_number_visible(self):
        return self.find(self.version_number).is_displayed()

    def get_dashboard_title_style(self, property_name):
        title_element = self.find(self.dashboard_title)
        return title_element.value_of_css_property(property_name)
