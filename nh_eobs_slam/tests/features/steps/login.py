from behave import given
from openeobs_mobile.login_page import LoginPage
from openeobs_selenium.environment import MOB_LOGIN, NURSE_USERNM1, \
    NURSE_PWD1, HCA_USERNM1, HCA_PWD1


@given('I am logged in as a {user}')
def login(context, user):
    context.browser.get(MOB_LOGIN)
    context.login_page = LoginPage(context.browser)

    # TOOD: Move HCA foo into lib
    user_dict = {
        'Nurse': (NURSE_USERNM1, NURSE_PWD1),
        'HCA': (HCA_USERNM1, HCA_PWD1)
    }
    user_login = user_dict.get(user)
    if user_login:
        context.login_page.login(
            *user_login, database=context.test_database_name)
    assert(context.login_page.has_logged_in())
