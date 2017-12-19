from behave import given, when, then
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as ec
from openeobs_mobile.task_page import TaskPage
from openeobs_mobile.list_page import ListPage
from openeobs_mobile.task_page_locators import SUCCESSFUL_SUBMIT, \
    CONFIRM_ACTION_TAKEN, CONFIRM_TASK, CONFIRM_ACTION, RELATED_TASK_LIST, \
    RELATED_TASK, CANCEL_SUBMIT, CANCEL_TASK, CANCEL_POPUP, CANCEL_SELECT, \
    CANCEL_COMPLETE, TASK, FREQUENCY_SELECT
from openeobs_mobile.page_confirm import PageConfirm
from openeobs_mobile.list_page_locators import LIST_ITEM_PATIENT_NAME, \
    LIST_ITEM_DEADLINE


@given('I am shown the triggered tasks popup')
@when('I am shown the triggered tasks popup')
def task_popup(context):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(SUCCESSFUL_SUBMIT)
    )
    successful_submit = context.browser.find_element(*SUCCESSFUL_SUBMIT)

    assert(successful_submit.is_displayed())


@when('I click the Assess Patient notification item')
def click_notification(context):

    related_task = context.browser.find_element(*CONFIRM_TASK)
    assert(related_task is not None)
    related_task.click()


@then('I can confirm the notification')
def can_confirm(context):
    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CONFIRM_ACTION)
    )
    submit_button = context.browser.find_element(*CONFIRM_ACTION)
    assert(submit_button is not None)


@when('I confirm the Assess Patient notification')
@given('I confirm the Assess Patient notification')
def confirm_notification(context):
    task_popup(context)
    click_notification(context)
    can_see_task(context, 'Assess Patient')
    can_confirm(context)

    context.browser.find_element(*CONFIRM_ACTION).click()

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(SUCCESSFUL_SUBMIT)
    )
    success = context.browser.find_element(*SUCCESSFUL_SUBMIT)
    assert(success is not None)


# @when('I click the Call Ambulance notification item')
# @given('I click the Call Ambulance notification item')
# def select_ambulance_item(context):
#     ui.WebDriverWait(context.browser, 5).until(
#         ec.visibility_of_element_located(RELATED_TASK_LIST)
#     )
#     related_tasks = context.browser.find_elements(*RELATED_TASK_LIST)
#     assert(len(related_tasks) > 0)
#     for task in related_tasks:
#         if task.text == 'Call An Ambulance 2222/9999':
#             task.click()
#             break


@then('I can cancel the notification')
def can_cancel(context):
    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CANCEL_SUBMIT)
    )
    cancel_button = context.browser.find_element(*CANCEL_SUBMIT)
    assert (cancel_button is not None)


@then('I should not see any triggered tasks when I confirm the notification')
def no_triggered_tasks(context):
    context.browser.find_element(*CONFIRM_ACTION).click()

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(RELATED_TASK)
    )
    related_task = context.browser.find_element(*RELATED_TASK)
    assert('The notification was successfully submitted' in related_task.text)


@when('I cancel the notification')
def cancel_ambulance(context):
    context.browser.find_element(*CANCEL_SUBMIT).click()

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CANCEL_POPUP)
    )
    cancel_window = context.browser.find_element(*CANCEL_POPUP)
    assert(cancel_window is not None)


@then('I am shown a list of cancellation reason')
def cancel_reasons(context):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CANCEL_SELECT)
    )

    cancel = context.browser.find_element(*CANCEL_SELECT)
    assert (cancel is not None)


@then('I should not see any triggered tasks when I cancel the notification')
def no_triggered_tasks_cancelled(context):
    context.browser.find_element(*CANCEL_TASK).click()

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CANCEL_COMPLETE)
    )
    cancelled = context.browser.find_element(*CANCEL_COMPLETE)
    assert('The notification was successfully cancelled' in cancelled.text)


# @when('I click the Shift Coordinator notification item')
# def inform_shift_coordinator(context):
#     ui.WebDriverWait(context.browser, 5).until(
#         ec.visibility_of_element_located(RELATED_TASK_LIST)
#     )
#     related_tasks = context.browser.find_elements(*RELATED_TASK_LIST)
#     assert(len(related_tasks) > 0)
#     for task in related_tasks:
#         if task.text == 'Inform Shift Coordinator':
#             task.click()
#             break


@when('I go to the task list')
def go_to_task_list(context):
    task_page = TaskPage(context.browser)
    page_confirm = PageConfirm(context.browser)
    task_page.go_to_task_list()
    assert(page_confirm.is_task_list_page())


@then('I should see the following new notifications for the patient')
def check_task_list(context):
    patient_name = context.patient_name
    task_page = ListPage(context.browser)
    task_list = [
        task.find_element(*TASK).text for task in task_page.get_list_items()
        if task.find_element(*LIST_ITEM_PATIENT_NAME).text == patient_name]
    for row in context.table:
        assert(row.get('tasks') in task_list)


@then('the next NEWS observation task for the patient is in {time} {period}')
def check_next_ews(context, time, period):
    patient_name = context.patient_name
    page_confirm = PageConfirm(context.browser)
    task_page = ListPage(context.browser)
    task_page.go_to_patient_list()
    assert (page_confirm.is_patient_list_page())
    task_list = [
        task.find_element(*LIST_ITEM_DEADLINE).text for
        task in task_page.get_list_items()
        if task.find_element(*LIST_ITEM_PATIENT_NAME).text == patient_name]
    assert(len(task_list) == 1)
    time_range = range(int(time) - 1, int(time) + 1)
    if period == 'minutes':
        assert(int(task_list[0][3:][:2]) in time_range)
    else:
        assert(int(task_list[0][:2]) in time_range)


@then('I should see no new notifications for the patient')
def check_no_notifications(context):
    patient_name = context.patient_name
    page_confirm = PageConfirm(context.browser)
    task_page = ListPage(context.browser)
    task_page.go_to_task_list()
    assert (page_confirm.is_task_list_page())
    task_list = [
        task.find_element(*TASK).text for task in task_page.get_list_items()
        if task.find_element(*LIST_ITEM_PATIENT_NAME).text == patient_name]
    assert(len(task_list) == 0)


# @when('I click the Review Frequency notification item')
# def select_review_frequency(context):
#
#     ui.WebDriverWait(context.browser, 5).until(
#         ec.visibility_of_element_located(RELATED_TASK_LIST)
#     )
#     related_tasks = context.browser.find_elements(*RELATED_TASK_LIST)
#
#     assert(len(related_tasks) > 0)
#     for task in related_tasks:
#         if task.text == 'Review Frequency':
#             task.click()
#             break

@given('I click the {task_name} notification item')
@when('I click the {task_name} notification item')
def click_notification_item(context, task_name):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(RELATED_TASK_LIST)
    )
    related_tasks = context.browser.find_elements(*RELATED_TASK_LIST)

    assert(len(related_tasks) > 0)
    for task in related_tasks:
        if task.text == task_name:
            task.click()
            break


@then('I can see the text "{task_name}"')
def can_see_task(context, task_name):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CONFIRM_ACTION_TAKEN)
    )

    please_confirm = context.browser.find_element(*CONFIRM_ACTION_TAKEN).text
    assert (task_name in please_confirm)


@then('I can see a list of frequencies')
def frequency_list(context):

    frequency_field = context.browser.find_element(*FREQUENCY_SELECT)
    options = frequency_field.find_elements_by_tag_name('option')
    options_text = [value.text for value in options]

    for row in context.table:
        assert(row.get('frequency') in options_text)


@when('I confirm the Review Frequency notification')
def confirm_frequency(context):

    click_notification_item(context, 'Review Frequency')

    frequency_field = context.browser.find_element(*FREQUENCY_SELECT)
    options = frequency_field.find_elements_by_tag_name('option')
    options[1].click()

    context.browser.find_element(*CONFIRM_ACTION).click()

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(SUCCESSFUL_SUBMIT)
    )

    success_heading = context.browser.find_element(*SUCCESSFUL_SUBMIT).text
    assert('Submission successful' in success_heading)
