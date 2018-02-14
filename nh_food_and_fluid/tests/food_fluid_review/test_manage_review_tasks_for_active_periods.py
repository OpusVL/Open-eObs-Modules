# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestManageReviewTasksForActivePeriods(TransactionCase):
    """
    Inherits from TestCancelReviewTasks so that the same tests can be run again
    therefore asserting that the same state changes have occurred even when
    calling from a method lower down in the execution stack.
    """
    def setUp(self):
        super(TestManageReviewTasksForActivePeriods, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.activity_model = self.env['nh.activity']

        self.f_and_f_review_activity_id = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': self.spell_activity.id},
                {'patient_id': self.patient.id})
        self.f_and_f_review_activity = self.activity_model.browse(
            self.f_and_f_review_activity_id)

        self.datetime_utils = self.env['datetime_utils']

        def mock_get_localised_time(*args, **kwargs):
            return self.date_time
        self.datetime_utils._patch_method('get_localised_time',
                                          mock_get_localised_time)

    def tearDown(self):
        self.datetime_utils._revert_method('get_localised_time')
        super(TestManageReviewTasksForActivePeriods, self)\
            .tearDown()

    def call_test(self, date_time=None, spell_activity_id=None):
        if not date_time:
            date_time = datetime(1989, 6, 6, 14, 0, 0)
        self.date_time = date_time

        self.food_and_fluid_review_model \
            .manage_review_tasks_for_active_periods()

    def test_cancel_review_tasks_when_time_is_2pm_local_time(self):
        self.call_test(date_time=datetime(1989, 6, 6, 14, 0, 0))
        expected = 'cancelled'
        actual = self.f_and_f_review_activity.state
        self.assertEqual(expected, actual)

    def test_cancel_review_tasks_when_time_is_6am_local_time(self):
        self.call_test(date_time=datetime(1989, 6, 6, 6, 0, 0))
        expected = 'cancelled'
        actual = self.f_and_f_review_activity.state
        self.assertEqual(expected, actual)

    def test_does_not_cancel_review_tasks_at_other_times(self):
        self.call_test(date_time=datetime(1989, 6, 6, 7, 0, 0))
        expected = 'new'
        actual = self.f_and_f_review_activity.state
        self.assertEqual(expected, actual)

    def test_sets_cancel_reason_when_time_is_2pm_local_time(self):
        self.call_test(date_time=datetime(1989, 6, 6, 14, 0, 0))
        cancel_reason_6am_review = self.test_utils.browse_ref(
            'nh_food_and_fluid.cancel_reason_not_performed')

        expected = cancel_reason_6am_review.id
        actual = self.f_and_f_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)

    def test_sets_cancel_reason_when_time_is_6am_local_time(self):
        self.call_test(date_time=datetime(1989, 6, 6, 6, 0, 0))
        cancel_reason_not_performed = self.test_utils.browse_ref(
            'nh_food_and_fluid.cancel_reason_6am_review')

        expected = cancel_reason_not_performed.id
        actual = self.f_and_f_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)
