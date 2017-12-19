from openerp.addons.nh_eobs_api.tests.api_test_common import APITestCommon
from itertools import product
from openerp.addons.nh_eobs_api.routing import Route
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
import json
import requests
import openerp


class TestPartialObservationSubmissionScore(APITestCommon):
    """
    Test that the override of the form submission endpoint is returning the
    score and clinical risk
    """

    PORT = openerp.tools.config['xmlrpc_port']
    DB = openerp.tools.config['db_name']

    standard_values = {
        'respiration_rate': [18, None],
        'indirect_oxymetry_spo2': [100, None],
        'oxygen_administration_flag': [False, None],
        'body_temperature': [37.5, None],
        'blood_pressure_systolic': [120, None],
        'blood_pressure_diastolic': [None, None],
        'pulse_rate': [80, None],
        'avpu_text': ['A', None]
    }

    complete_values = {
        'respiration_rate': 18,
        'indirect_oxymetry_spo2': 100,
        'oxygen_administration_flag': False,
        'body_temperature': 37.5,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'pulse_rate': 80,
        'avpu_text': 'A'
    }

    EMPTY_PARTIAL = {
        'respiration_rate': None,
        'blood_pressure_diastolic': None,
        'blood_pressure_systolic': None,
        'body_temperature': None,
        'oxygen_administration_flag': None,
        'indirect_oxymetry_spo2': None,
        'avpu_text': None,
        'pulse_rate': None,
        'partial_reason': 'asleep'
    }

    LOW_PARTIAL = {
        'respiration_rate': 11,
        'blood_pressure_diastolic': None,
        'blood_pressure_systolic': None,
        'body_temperature': None,
        'oxygen_administration_flag': None,
        'indirect_oxymetry_spo2': None,
        'avpu_text': None,
        'pulse_rate': None,
        'partial_reason': 'asleep'
    }

    MED_PARTIAL = {
        'respiration_rate': 11,
        'blood_pressure_diastolic': None,
        'blood_pressure_systolic': None,
        'body_temperature': 38.0,
        'oxygen_administration_flag': None,
        'indirect_oxymetry_spo2': 91,
        'avpu_text': None,
        'pulse_rate': 50,
        'partial_reason': 'asleep'
    }

    HIGH_PARTIAL = {
        'respiration_rate': 11,
        'blood_pressure_diastolic': 110,
        'blood_pressure_systolic': 90,
        'body_temperature': 38.0,
        'oxygen_administration_flag': None,
        'indirect_oxymetry_spo2': 93,
        'avpu_text': 'A',
        'pulse_rate': 50,
        'partial_reason': 'asleep'
    }

    standard_combinations = list(product(*standard_values.values()))

    ews_keys = [
        'blood_pressure_diastolic',
        'blood_pressure_systolic',
        'body_temperature',
        'oxygen_administration_flag',
        'indirect_oxymetry_spo2',
        'respiration_rate',
        'avpu_text',
        'pulse_rate'
    ]

    def setUp(self):
        super(TestPartialObservationSubmissionScore, self).setUp()
        combinations = []
        for combo in self.standard_combinations:
            vals = {}
            for index, val in enumerate(combo):
                vals[self.ews_keys[index]] = val
            vals['partial_reason'] = 'asleep'
            if vals['blood_pressure_systolic'] == 120:
                vals['blood_pressure_diastolic'] = 80
            complete = set(vals.items() +
                           self.complete_values.items())
            if any(combo) and len(complete) > 9:
                combinations.append(vals)
        self.combinations = combinations

    def test_no_risk_partial_patient(self):
        """
        Test that the server returns the score and clinical risk in the message
        for patient endpoint
        """
        for wombo_combo in self.combinations:
            route_under_test = \
                route_manager.get_route('json_patient_form_action')
            self.assertIsInstance(route_under_test, Route)
            patient_list = self.mock_get_patients()
            patient_id = patient_list[0].get('id')

            api_pool = self.registry('nh.eobs.api')
            activity_pool = self.registry('nh.activity')

            # mock out api.create_activity
            def mock_create_activity(*args, **kwargs):
                return 1
            api_pool._patch_method('create_activity_for_patient',
                                   mock_create_activity)

            # mock out api.complete
            def mock_complete(*args, **kwargs):
                return True
            api_pool._patch_method('complete', mock_complete)

            # mock out search for triggered activities
            def mock_activity_search(*args, **kwargs):
                return []
            activity_pool._patch_method('search', mock_activity_search)
            activity_pool._patch_method('read', mock_activity_search)

            test_resp = requests.post(
                '{0}{1}/patient/submit_ajax/ews/{2}'.format(
                    route_manager.BASE_URL,
                    route_manager.URL_PREFIX,
                    patient_id
                ),
                data=wombo_combo,
                cookies=self.auth_resp.cookies
            )

            api_pool._revert_method('create_activity_for_patient')
            api_pool._revert_method('complete')
            activity_pool._revert_method('search')
            activity_pool._revert_method('read')
            self.assertEqual(test_resp.status_code, 200)
            self.assertEqual(test_resp.headers['content-type'],
                             'application/json')
            patient_data = json.loads(test_resp.content)
            patient_message = patient_data.get('description')
            self.assertEqual(
                patient_message,
                '<strong>At least No clinical risk</strong>, '
                'real risk may be higher <br>'
                '<strong>At least 0 NEWS score</strong>, '
                'real NEWS score may be higher<br>'
                'This Partial Observation will not update the NEWS score and '
                'clinical risk of the patient')

    def test_no_risk_partial_task(self):
        """
        Test that the server returns the score and clinical risk in the message
        for task endpoint
        """
        for wombo_combo in self.combinations:
            route_under_test = \
                route_manager.get_route('json_task_form_action')
            self.assertIsInstance(route_under_test, Route)

            api_pool = self.registry('nh.eobs.api')
            activity_pool = self.registry('nh.activity')

            # mock out api.complete
            def mock_complete(*args, **kwargs):
                return True
            api_pool._patch_method('complete', mock_complete)

            # mock out search for triggered activities
            def mock_activity_search(*args, **kwargs):
                return []
            activity_pool._patch_method('search', mock_activity_search)
            activity_pool._patch_method('read', mock_activity_search)

            test_resp = requests.post(
                '{0}{1}/tasks/submit_ajax/ews/{2}'.format(
                    route_manager.BASE_URL,
                    route_manager.URL_PREFIX,
                    666
                ),
                data=wombo_combo,
                cookies=self.auth_resp.cookies
            )

            api_pool._revert_method('complete')
            activity_pool._revert_method('search')
            activity_pool._revert_method('read')
            self.assertEqual(test_resp.status_code, 200)
            self.assertEqual(test_resp.headers['content-type'],
                             'application/json')
            patient_data = json.loads(test_resp.content)
            patient_message = patient_data.get('description')
            self.assertEqual(
                patient_message,
                '<strong>At least No clinical risk</strong>, '
                'real risk may be higher <br>'
                '<strong>At least 0 NEWS score</strong>, '
                'real NEWS score may be higher<br>'
                'This Partial Observation will not update the NEWS score and '
                'clinical risk of the patient')

    def test_low_risk_partial_task(self):
        """
        Test submitting a partial that would score low clinical risk on task
        endpoint
        """

        route_under_test = \
            route_manager.get_route('json_task_form_action')
        self.assertIsInstance(route_under_test, Route)

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/tasks/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                666
            ),
            data=self.LOW_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least Low clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 1 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_low_risk_partial_patient(self):
        """
        Test that the server returns the score and clinical risk in the message
        for patient endpoint
        """
        route_under_test = \
            route_manager.get_route('json_patient_form_action')
        self.assertIsInstance(route_under_test, Route)
        patient_list = self.mock_get_patients()
        patient_id = patient_list[0].get('id')

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.create_activity
        def mock_create_activity(*args, **kwargs):
            return 1

        api_pool._patch_method('create_activity_for_patient',
                               mock_create_activity)

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/patient/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                patient_id
            ),
            data=self.LOW_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('create_activity_for_patient')
        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least Low clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 1 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_med_risk_partial_task(self):
        """
        Test submitting a partial that would score low clinical risk on task
        endpoint
        """

        route_under_test = \
            route_manager.get_route('json_task_form_action')
        self.assertIsInstance(route_under_test, Route)

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/tasks/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                666
            ),
            data=self.MED_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least Medium clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 5 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_med_risk_partial_patient(self):
        """
        Test that the server returns the score and clinical risk in the message
        for patient endpoint
        """
        route_under_test = \
            route_manager.get_route('json_patient_form_action')
        self.assertIsInstance(route_under_test, Route)
        patient_list = self.mock_get_patients()
        patient_id = patient_list[0].get('id')

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.create_activity
        def mock_create_activity(*args, **kwargs):
            return 1

        api_pool._patch_method('create_activity_for_patient',
                               mock_create_activity)

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/patient/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                patient_id
            ),
            data=self.MED_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('create_activity_for_patient')
        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least Medium clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 5 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_high_risk_partial_task(self):
        """
        Test submitting a partial that would score low clinical risk on task
        endpoint
        """

        route_under_test = \
            route_manager.get_route('json_task_form_action')
        self.assertIsInstance(route_under_test, Route)

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/tasks/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                666
            ),
            data=self.HIGH_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least High clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 7 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_high_risk_partial_patient(self):
        """
        Test that the server returns the score and clinical risk in the message
        for patient endpoint
        """
        route_under_test = \
            route_manager.get_route('json_patient_form_action')
        self.assertIsInstance(route_under_test, Route)
        patient_list = self.mock_get_patients()
        patient_id = patient_list[0].get('id')

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.create_activity
        def mock_create_activity(*args, **kwargs):
            return 1

        api_pool._patch_method('create_activity_for_patient',
                               mock_create_activity)

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/patient/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                patient_id
            ),
            data=self.HIGH_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('create_activity_for_patient')
        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>At least High clinical risk</strong>, '
            'real risk may be higher <br>'
            '<strong>At least 7 NEWS score</strong>, '
            'real NEWS score may be higher<br>'
            'This Partial Observation will not update the NEWS score and '
            'clinical risk of the patient')

    def test_empty_partial_task(self):
        """
        Test submitting a partial that would score low clinical risk on task
        endpoint
        """

        route_under_test = \
            route_manager.get_route('json_task_form_action')
        self.assertIsInstance(route_under_test, Route)

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/tasks/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                666
            ),
            data=self.EMPTY_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>Clinical risk:</strong> Unknown<br>'
            '<strong>NEWS Score:</strong> Unknown<br>'
            'This Partial Observation will not update the '
            'NEWS score and clinical risk of the patient')

    def test_empty_partial_patient(self):
        """
        Test that the server returns the score and clinical risk in the message
        for patient endpoint
        """
        route_under_test = \
            route_manager.get_route('json_patient_form_action')
        self.assertIsInstance(route_under_test, Route)
        patient_list = self.mock_get_patients()
        patient_id = patient_list[0].get('id')

        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        # mock out api.create_activity
        def mock_create_activity(*args, **kwargs):
            return 1

        api_pool._patch_method('create_activity_for_patient',
                               mock_create_activity)

        # mock out api.complete
        def mock_complete(*args, **kwargs):
            return True

        api_pool._patch_method('complete', mock_complete)

        # mock out search for triggered activities
        def mock_activity_search(*args, **kwargs):
            return []

        activity_pool._patch_method('search', mock_activity_search)
        activity_pool._patch_method('read', mock_activity_search)

        test_resp = requests.post(
            '{0}{1}/patient/submit_ajax/ews/{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                patient_id
            ),
            data=self.EMPTY_PARTIAL,
            cookies=self.auth_resp.cookies
        )

        api_pool._revert_method('create_activity_for_patient')
        api_pool._revert_method('complete')
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')
        patient_data = json.loads(test_resp.content)
        patient_message = patient_data.get('description')
        self.assertEqual(
            patient_message,
            '<strong>Clinical risk:</strong> Unknown<br>'
            '<strong>NEWS Score:</strong> Unknown<br>'
            'This Partial Observation will not update the '
            'NEWS score and clinical risk of the patient')
