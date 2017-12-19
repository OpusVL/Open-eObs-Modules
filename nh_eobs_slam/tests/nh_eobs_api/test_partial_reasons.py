from openerp.tests.common import SingleTransactionCase, HttpCase


class TestPartialReasons(SingleTransactionCase):
    """
    Test that the partial reasons for observations are updated to SLaM's
    preferences
    """

    @classmethod
    def setUpClass(cls):
        super(TestPartialReasons, cls).setUpClass()
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')

    def test_ews_partial_reasons(self):
        """
        TEst that the partial reasons returned for EWS are those SLaM wants
        """
        reasons = self.ews_pool._partial_reasons
        self.assertEqual(reasons, [
            ['asleep', 'Asleep'],
            ['refused', 'Refused'],
            ['request_by_doctor', 'Request By Doctor'],
            ['patient_aggression', 'Patient Aggression']
        ])


class TestPartialReasonsMobile(HttpCase):
    """
    Test that the partial reasons returned on the mobile are updated to SLaM's
    Preferences
    """

    def test_ews_partial_reasons_endpoint(self):
        """
        Test that the /ews/partial_reasons endpoint returns the reasons SLaM
        wants
        """
        self.authenticate('admin', 'admin')
        reasons = self.url_open('/api/v1/ews/partial_reasons').read()
        self.assertEqual(
            reasons,
            '{"status": "success", "data": '
            '[["asleep", "Asleep"], '
            '["refused", "Refused"], '
            '["request_by_doctor", "Request By Doctor"], '
            '["patient_aggression", "Patient Aggression"]'
            '], '
            '"description": "Please state reason for '
            'submitting partial observation", '
            '"title": "Reason for partial observation"}')
