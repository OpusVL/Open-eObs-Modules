# -*- coding: utf-8 -*-
import copy

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestReviewFrequencyGetFormDescription(TransactionCase):

    def setUp(self):
        super(TestReviewFrequencyGetFormDescription, self).setUp()
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
        self.test_utils.complete_obs(clinical_risk_sample_data.NO_RISK_DATA,
                                     self.open_obs_activity.id)
        ews_activity = self.test_utils.ews_activity
        triggered_task = \
            self.test_utils.get_open_task_triggered_by(ews_activity.id)
        form_desc = \
            triggered_task.data_ref.get_form_description(self.patient_id) \
            if triggered_task else None
        self.assertFalse(form_desc)

    def test_form_desc_after_low_risk(self):
        """
        Test that after completing a new NEWS observation with low clinical
        risk it shows the message and cancel button
        """
        self.test_utils.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA,
                                     self.open_obs_activity.id)
        ews_activity = self.test_utils.ews_activity
        triggered_task = \
            self.test_utils.get_open_task_triggered_by(ews_activity.id)
        form_desc = \
            triggered_task.data_ref.get_form_description(self.patient_id) \
            if triggered_task else None
        self.assertFalse(form_desc)

    def test_form_desc_after_medium_risk(self):
        """
        Test that after completing a new NEWS observation with medium clinical
        risk it shows the message and cancel button
        """
        self.test_utils.complete_obs(
            clinical_risk_sample_data.MEDIUM_RISK_DATA,
            self.open_obs_activity.id)
        ews_activity = self.test_utils.ews_activity
        triggered_task = \
            self.test_utils.get_open_task_triggered_by(ews_activity.id)
        form_desc = \
            triggered_task.data_ref.get_form_description(self.patient_id) \
            if triggered_task else None
        self.assertFalse(form_desc)

    def test_form_desc_after_high_risk(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk it shows the message and cancel button
        """
        self.test_utils.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA,
                                     self.open_obs_activity.id)
        ews_activity = self.test_utils.ews_activity
        triggered_task = \
            self.test_utils.get_open_task_triggered_by(ews_activity.id)
        form_desc = \
            triggered_task.data_ref.get_form_description(self.patient_id) \
            if triggered_task else None
        self.assertFalse(form_desc)

    def test_form_desc_after_partial_obs(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk it shows the message and cancel button
        """
        no_risk_data = copy.deepcopy(clinical_risk_sample_data.NO_RISK_DATA)
        del no_risk_data['respiration_rate']
        no_risk_data['partial_reason'] = 'asleep'

        self.test_utils.complete_obs(no_risk_data,
                                     self.open_obs_activity.id)
        form_desc = \
            self.frequency_notification.get_form_description(self.patient_id)
        self.assertTrue(form_desc)
        form_desc = form_desc[0]
        self.assertEqual(form_desc.get('label'), 'Observation frequency')
        self.assertEqual(form_desc.get('name'), 'frequency')
        self.assertEqual(form_desc.get('type'), 'selection')
        self.assertTrue(len(form_desc.get('selection')) > 1)
