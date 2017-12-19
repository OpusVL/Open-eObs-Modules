from selenium import webdriver
from erppeek import Client
import openeobs_selenium.environment
from openeobs_selenium.environment import ODOO_CLIENT_URL, USERNAME, \
    PASSWORD, TEST_DB_NAME, DATABASE
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
import selenium.webdriver.support.ui as ui


def before_all(context):
    context.browser = webdriver.PhantomJS()
    context.browser.set_window_size(1920, 1080)
    openeobs_selenium.environment.DATABASE = 'slam'
    context.browser.get(openeobs_selenium.environment.get_desktop_url())
    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR,
                                          '.oe_single_form_container.'
                                          'modal-content'))
    )
    context.odoo_client = Client(ODOO_CLIENT_URL,
                                 db=DATABASE,
                                 user=USERNAME,
                                 password=PASSWORD)
    context.test_database_name = TEST_DB_NAME

# def after_step(context, step):
#     if step.status == 'failed':
#         import pdb
#         pdb.set_trace()


def before_feature(context, feature):
    if context.test_database_name in context.odoo_client.db.list():
        context.odoo_client.db.drop('admin', context.test_database_name)
    context.odoo_client.db.duplicate_database('admin', DATABASE,
                                              context.test_database_name)
    context.odoo_client.login(USERNAME, password=PASSWORD,
                              database=context.test_database_name)


def after_all(context):
    context.odoo_client.db.drop('admin', context.test_database_name)
    context.browser.close()
