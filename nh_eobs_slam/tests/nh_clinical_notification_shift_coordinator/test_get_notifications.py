# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetNotifications(TransactionCase):
    def setUp(self):
        super(TestGetNotifications, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.activity_model = self.env['nh.activity']

    def call_test(self, risks):
        for risk in risks:
            ews_activity = self.test_utils.sudo(self.test_utils.nurse)\
                .create_and_complete_ews_obs_activity(
                self.patient.id, self.spell.id, risk=risk)

            if risks.index(risk) == 0:
                first_ews_activity = ews_activity

        triggered_tasks = first_ews_activity.data_ref.get_triggered_tasks()
        self.assertEqual(1, len(triggered_tasks))
        return triggered_tasks[0]

    def test_low_risk_triggered_task_when_current_risk_is_high(self):
        """
        Test that a review frequency task is triggered by completion of the
        low risk assess patient task even when the clinical risk has since
        changed to 'high' and a separate 'flow' of escalation tasks for that
        newer clinical risk are open.
        """
        assess_patient = self.call_test(['low', 'high'])

        activity_id = assess_patient['id']
        inform_shift_coordinator = \
            self.test_utils.complete_task_and_get_triggered(activity_id)

        activity_id = inform_shift_coordinator['id']
        triggered_task_inform_shift_coordinator = \
            self.test_utils.complete_task_and_get_triggered(activity_id)

        expected = 'nh.clinical.notification.frequency'
        actual = triggered_task_inform_shift_coordinator.data_model
        self.assertEqual(expected, actual)

    def test_medium_risk_triggered_task_when_current_risk_is_low(
            self):
        """
        Test that an inform medical team task is triggered by completion of the
        medium risk inform shift coordinator task even when the clinical risk
        has since changed to 'low' and a separate 'flow' of escalation tasks
        for that newer clinical risk are open.
        """
        inform_shift_coordinator = self.call_test(
            ['medium', 'low'])

        activity_id = inform_shift_coordinator['id']
        tasks_triggered_from_task = \
            self.test_utils.complete_task_and_get_triggered(activity_id)

        expected = 'nh.clinical.notification.medical_team'
        actual = tasks_triggered_from_task.data_model
        self.assertEqual(expected, actual)

    def test_high_risk_triggered_task_when_current_risk_is_low(
            self):
        """
        Test that an inform medical team task is triggered by completion of the
        high risk inform shift coordinator task even when the clinical risk
        has since changed to 'low' and a separate 'flow' of escalation tasks
        for that newer clinical risk are open.
        """
        inform_shift_coordinator = self.call_test(
            ['high', 'low'])

        activity_id = inform_shift_coordinator['id']
        tasks_triggered_from_task = \
            self.test_utils.complete_task_and_get_triggered(activity_id)

        expected = 'nh.clinical.notification.medical_team'
        actual = tasks_triggered_from_task.data_model
        self.assertEqual(expected, actual)
