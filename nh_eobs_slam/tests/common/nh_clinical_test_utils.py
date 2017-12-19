from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def complete_inform_shift_coordinator(self, user_id=None):
        self.complete_open_activity(
            'nh.clinical.notification.shift_coordinator', user_id=user_id)

    def complete_inform_medical_team(self, user_id=None):
        self.complete_open_activity(
            'nh.clinical.notification.medical_team', user_id=user_id)

    def cancel_inform_medical_team(self, user_id=None):
        self.cancel_open_activity(
            'nh.clinical.notification.medical_team', user_id=user_id)

    def complete_call_ambulance(self, user_id=None):
        self.complete_open_activity(
            'nh.clinical.notification.ambulance', user_id=user_id)

    def cancel_call_ambulance(self, user_id=None):
        self.cancel_open_activity(
            'nh.clinical.notification.ambulance', user_id=user_id)

    def complete_assess_patient(self, user_id=None):
        self.complete_open_activity(
            'nh.clinical.notification.assessment', user_id=user_id)

    def complete_frequency(self, user_id=None, frequency=None):
        if frequency:
            vals = {'frequency': frequency}
        else:
            vals = None
        self.complete_open_activity(
            'nh.clinical.notification.frequency', user_id=user_id, vals=vals)

    def cancel_frequency(self, user_id=None):
        task = self.cancel_open_activity(
            'nh.clinical.notification.frequency', user_id=user_id)
        return task

    def complete_frequency_agreed(self, user_id=None):
        self.complete_open_activity(
            'nh.clinical.notification.frequency_agreed', user_id=user_id)

    def cancel_frequency_agreed(self, user_id=None):
        self.cancel_open_activity(
            'nh.clinical.notification.frequency_agreed', user_id=user_id)

    def complete_task_and_get_triggered(self, activity_id):
        """
        Complete the task with the passed activity ID and return the task
        triggered by its completion.
        :param activity_id:
        :type activity_id: int
        :return:
        """
        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)
        activity.complete(activity_id)

        triggered_tasks = activity.data_ref.get_triggered_tasks()
        if len(triggered_tasks) != 1:
            raise AssertionError("Did not expect more than one triggered "
                                 "task.")
        return triggered_tasks[0]