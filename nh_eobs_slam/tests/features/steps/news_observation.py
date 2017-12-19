from behave import given, then
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as ec
from openeobs_mobile.list_page import ListPage
from openeobs_mobile.list_page_locators import LIST_ITEM_PATIENT_NAME
from openeobs_mobile.page_confirm import PageConfirm
from openeobs_mobile.patient_page import PatientPage
from openeobs_mobile.observation_form_page import ObservationFormPage
from openeobs_mobile.patient_page_locators import OPEN_OBS_MENU_NEWS_ITEM
from openeobs_mobile.task_page_locators import CONFIRM_SUBMIT, RELATED_TASK,\
    CLINICAL_RISK
from openeobs_mobile.data import NO_RISK_EWS_DATA, LOW_RISK_SCORE_1_EWS_DATA, \
    MEDIUM_RISK_SCORE_5_EWS_DATA, HIGH_RISK_SCORE_7_EWS_DATA
from openeobs_selenium.environment import PATIENT_PAGE
from datetime import datetime, timedelta
import time


@given("I submit a NEWS Observation for a patient "
       "with {clinical_risk} clinical risk")
def submit_observation(context, clinical_risk):

    risk_dict = {
        'no': NO_RISK_EWS_DATA,
        'a low': LOW_RISK_SCORE_1_EWS_DATA,
        'a medium': MEDIUM_RISK_SCORE_5_EWS_DATA,
        'a high': HIGH_RISK_SCORE_7_EWS_DATA
    }
    risk_score = risk_dict.get(clinical_risk)
    if not risk_score:
        raise ValueError('No risk score available')

    page_confirm = PageConfirm(context.browser)
    patient_list_page = ListPage(context.browser)

    patient_list_page.go_to_patient_list()
    assert(page_confirm.is_patient_list_page())
    patients = patient_list_page.get_list_items()

    PatientPage(context.browser).select_patient(patients)
    PatientPage(context.browser).open_form(OPEN_OBS_MENU_NEWS_ITEM)
    ObservationFormPage(context.browser).enter_obs_data(risk_score)


@given('I confirm the calculated clinical risk to be {clinical_risk}')
def confirm_observation(context, clinical_risk):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CLINICAL_RISK)
    )
    risk_string = context.browser.find_element(*CLINICAL_RISK)

    assert(risk_string.text == 'Clinical risk: {0}'.format(clinical_risk))

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(CONFIRM_SUBMIT)
    )

    context.browser.find_element(*CONFIRM_SUBMIT).click()


@then('I should see no triggered tasks')
def no_task(context):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(RELATED_TASK)
    )

    related_task = context.browser.find_element(*RELATED_TASK)

    assert(related_task.text == '')


@then('I should see these triggered tasks')
@then('I see a popup with the following notifications')
def triggered_task(context):

    ui.WebDriverWait(context.browser, 5).until(
        ec.visibility_of_element_located(RELATED_TASK)
    )
    related_task = context.browser.find_element(*RELATED_TASK)
    tasks = related_task.text
    for row in context.table:
        assert(row.get('tasks') in tasks)


@given('I submit a NEWS Observation for a patient with {risk} clinical risk '
       'who has been in hospital for {stay_duration} days')
def submit_extended_obs(context, risk, stay_duration):

    durations = {
        '1-2': 1,
        '3+': 5
    }
    risk_triggered_acts = {
        'no': [],
        'a low': [
            'nh.clinical.notification.assessment',
            'nh.clinical.notification.hca',
            'nh.clinical.notification.nurse'
        ],
        'a medium': [
            'nh.clinical.notification.hca',
            'nh.clinical.notification.nurse',
            'nh.clinical.notification.shift_coordinator',
            'nh.clinical.notification.medical_team',
            'nh.clinical.notification.ambulance'
        ],
        'a high': [
            'nh.clinical.notification.hca',
            'nh.clinical.notification.nurse',
            'nh.clinical.notification.shift_coordinator',
            'nh.clinical.notification.medical_team',
            'nh.clinical.notification.ambulance'
        ]
    }

    spell_model = context.odoo_client.model('nh.clinical.spell')
    page_confirm = PageConfirm(context.browser)
    patient_list_page = ListPage(context.browser)

    patient_list_page.go_to_patient_list()
    assert(page_confirm.is_patient_list_page())
    patients = patient_list_page.get_list_items()

    patient = patients[0]
    patient_id = patient.get_attribute('href').replace(
        PATIENT_PAGE, ''
    )
    patient_name = patient.find_element(*LIST_ITEM_PATIENT_NAME)
    context.patient_name = patient_name.text
    spell_id = spell_model.get_by_patient_id(int(patient_id))
    tasks_to_cancel = risk_triggered_acts.get(risk)
    if tasks_to_cancel:
        patient_list_page.remove_tasks_for_patient(
            patient_id, tasks_to_cancel, database=context.test_database_name)
    present = datetime.now()
    days_ago = timedelta(days=durations.get(stay_duration))
    new_date = present - days_ago
    new_date_str = new_date.strftime('%Y-%m-%d %H:%M:00')
    spell_model.write(spell_id, {
        'date_started': new_date_str,
        'start_date': new_date_str,
    })
    read_date = spell_model.read(spell_id, ['date_started', 'start_date'])
    assert(read_date['date_started'] == new_date_str)
    assert(read_date['start_date'] == new_date_str)
    time.sleep(1)
    submit_observation(context, risk)
