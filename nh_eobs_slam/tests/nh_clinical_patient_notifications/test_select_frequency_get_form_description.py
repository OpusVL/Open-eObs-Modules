import copy

from openerp.addons.nh_eobs_slam.tests \
    .nh_clinical_patient_observation_ews.test_no_risk import \
    TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo as sevenplusdays
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestSelectFrequencyGetFormDescription(sevenplusdays):
    """
    Test that on:
    1. Submitting a no risk NEWS for a patient with a spell older than 7 days
    3. Not completing the triggered Select Frequency task
    4. Submitting another NEWS
    5. Opening the originally triggered Select Frequency will show a message
    and a cancel button instead of the frequency list
    """

    def setUp(self):
        super(TestSelectFrequencyGetFormDescription, self).setUp()
        activity_model = self.env['nh.activity']
        self.frequency_notification = \
            activity_model.browse(self.triggered_ids[0]).data_ref
        self.first_ews_activity_id = self.ews_activity_id
        ews_activity_search = self.activity_pool.search(
            self.cr,
            self.uid,
            [
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['patient_id', '=', self.patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if ews_activity_search:
            self.ews_activity_id = ews_activity_search[0]

    def test_no_weekly_frequency_agreed_notif_after_non_weekly_frequency(self):
        pass

    def test_form_desc_for_valid_task(self):
        """
        Test that without completing another NEWS observation that the form
        can be loaded
        """
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertTrue(form_desc)
        form_desc = form_desc[0]
        self.assertEqual(form_desc.get('label'), 'Observation frequency')
        self.assertEqual(form_desc.get('name'), 'frequency')
        self.assertEqual(form_desc.get('type'), 'selection')
        self.assertTrue(len(form_desc.get('selection')) > 1)

    def test_form_desc_after_no_risk(self):
        """
        Test that after completing a new NEWS observation with no clinical
        risk it shows the message and cancel button
        """
        self.complete_obs(clinical_risk_sample_data.NO_RISK_DATA)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertFalse(form_desc)

    def test_form_desc_after_low_risk(self):
        """
        Test that after completing a new NEWS observation with low clinical
        risk it shows the message and cancel button
        """
        self.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertFalse(form_desc)

    def test_form_desc_after_medium_risk(self):
        """
        Test that after completing a new NEWS observation with medium clinical
        risk it shows the message and cancel button
        """
        self.complete_obs(clinical_risk_sample_data.MEDIUM_RISK_DATA)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertFalse(form_desc)

    def test_form_desc_after_high_risk(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk it shows the message and cancel button
        """
        self.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertFalse(form_desc)

    def test_form_desc_after_partial_obs(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk it shows the message and cancel button
        """
        obs = copy.deepcopy(clinical_risk_sample_data.NO_RISK_DATA)
        del obs['respiration_rate']
        obs['partial_reason'] = 'asleep'
        self.complete_obs(obs)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertTrue(form_desc)
        form_desc = form_desc[0]
        self.assertEqual(form_desc.get('label'), 'Observation frequency')
        self.assertEqual(form_desc.get('name'), 'frequency')
        self.assertEqual(form_desc.get('type'), 'selection')
        self.assertTrue(len(form_desc.get('selection')) > 1)
