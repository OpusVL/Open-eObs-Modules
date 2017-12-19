import copy

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestReviewFrequencyIsValid(TransactionCase):

    def setUp(self):
        super(TestReviewFrequencyIsValid, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.activity_model = self.env['nh.activity']

        self.test_utils.admit_and_place_patient()
        self.nurse = self.test_utils.nurse
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA)
        self.test_utils.complete_assess_patient()
        self.test_utils.complete_inform_shift_coordinator()

        frequency_notification_activities = \
            self.test_utils.get_open_tasks('frequency')
        self.assertEqual(1, len(frequency_notification_activities))
        self.frequency_notification = \
            frequency_notification_activities[0].data_ref

        self.test_utils.get_open_obs()
        self.open_obs_activity = self.test_utils.ews_activity
        self.patient_id = self.test_utils.patient_id

    def test_valid_task(self):
        """
        Test that without completing another NEWS observation that the
        notification is considered valid
        """
        self.assertTrue(self.frequency_notification.is_valid())

    def test_validity_after_no_risk(self):
        """
        Test that after completing a new NEWS observation with no clinical
        risk that the notification is considered invalid
        """
        self.test_utils.complete_obs(clinical_risk_sample_data.NO_RISK_DATA,
                                     self.open_obs_activity.id)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_low_risk(self):
        """
        Test that after completing a new NEWS observation with low clinical
        risk that the notification is considered invalid
        """
        self.test_utils.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA,
                                     self.open_obs_activity.id)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_medium_risk(self):
        """
        Test that after completing a new NEWS observation with medium clinical
        risk that the notification is considered invalid
        """
        self.test_utils.complete_obs(
            clinical_risk_sample_data.MEDIUM_RISK_DATA,
            self.open_obs_activity.id
        )
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_high_risk(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk that the notification is considered invalid
        """
        self.test_utils.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA,
                                     self.open_obs_activity.id)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_partial_obs(self):
        """
        Test that after completing a partial observation that the notification
        isn't considered invalid
        """
        obs_data = copy.deepcopy(clinical_risk_sample_data.NO_RISK_DATA)
        del obs_data['respiration_rate']
        obs_data['partial_reason'] = 'asleep'
        self.test_utils.complete_obs(obs_data,
                                     self.open_obs_activity.id)
        self.assertTrue(self.frequency_notification.is_valid())
