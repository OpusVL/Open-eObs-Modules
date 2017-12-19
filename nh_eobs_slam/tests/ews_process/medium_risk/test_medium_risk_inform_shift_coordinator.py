from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase
import json


class TestMediumRiskInformShiftCoordinator(TransactionCase):
    """
    Test that the Inform Shift Coordinator task is generated for the Nurse on
    a Medium Risk EWS observation being completed
    """

    def setUp(self):
        super(TestMediumRiskInformShiftCoordinator, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.nurse = self.test_utils.nurse
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(
            clinical_risk_sample_data.MEDIUM_RISK_DATA)
        self.data_model = 'nh.clinical.notification.shift_coordinator'
        self.act_summary = 'Inform Shift Coordinator'

    def check_number_of_activities(self, expected_number, user_id=None):
        """
        Helper function to get list of activities and ensure correct number

        :param expected_number: Number of open activities we expect
        :param user_id: User to check for activities with
        """
        if not user_id:
            user_id = self.nurse.id
        activities = self.test_utils.get_open_activities_for_patient(
            data_model=self.data_model,
            user_id=user_id
        )
        self.assertEqual(len(activities.ids), expected_number)

    def test_inform_shift_coordinator_task_create(self):
        """
        Test that the Inform Shift Coordinator task is created after completing
        a high risk EWS
        """
        self.check_number_of_activities(1)

    def test_inform_shift_coordinator_task_after_pme(self):
        """
        Test that the Inform Shift Coordinator task is no longer available
        after PME
        """
        self.check_number_of_activities(1)
        self.test_utils.start_pme()
        # TODO: Eckhard to clarify if this should be 0 as EWS are cancelled on
        # PME
        self.check_number_of_activities(1)

    def test_inform_shift_coordinator_task_after_transfer_out(self):
        """
        Test that when transferring patient to another ward the user is no
        longer associated with the tasks
        """
        self.check_number_of_activities(1)
        self.test_utils.transfer_patient('WB')
        self.check_number_of_activities(0)

    def test_inform_shift_coordinator_task_after_transfer_in(self):
        """
        Test that when patient is transferred into ward that the escalation
        tasks are also transferred (current behaviour, would expect cancelled)
        """
        # TODO: Eckhard to clarify correct behaviour
        bed = self.test_utils.other_bed.id
        other_nurse = self.test_utils.create_nurse(bed)
        self.check_number_of_activities(1)
        self.test_utils.transfer_patient('WB')
        self.test_utils.place_patient(bed)
        self.check_number_of_activities(1, user_id=other_nurse.id)

    def test_inform_shift_coordinator_task_after_partial(self):
        """
        Test that after a partial observation the Nurse should still see
        the Inform Shift Coordinator task
        """
        self.check_number_of_activities(1)
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(
            clinical_risk_sample_data.PARTIAL_DATA_ASLEEP)
        self.check_number_of_activities(1)

    def test_inform_shift_coordinator_task_after_refusal(self):
        """
        Test that after a refused observation the Nurse should still see the
        Inform Shift Coordinator task
        """
        self.check_number_of_activities(1)
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.REFUSED_DATA)
        self.check_number_of_activities(1)

    def test_inform_shift_coordinator_task_on_workload_view(self):
        """
        Test that Inform Shift Coordinator task is visible in the workload view
        on the desktop
        """
        workload_model = self.env['nh.activity.workload']
        workload = workload_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.nurse.id]],
            ['date_scheduled', '!=', False],
            ['data_model', '=', self.data_model]
        ])
        self.assertEqual(len(workload.ids), 1)

    def test_inform_shift_coordinator_task_on_overdue_tasks_view(self):
        """
        Test that the Inform Shift Coordinator task is in the overdue tasks
        view when it's overdue
        """
        overdue_model = self.env['nh.clinical.overdue']
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.nurse.id]],
            ['data_model', '=', self.data_model]
        ])
        overdue_task = overdue_model.browse(task.id)
        self.assertEqual(overdue_task.delay, 0)

    def test_inform_shift_coordinator_task_on_report_in_progress(self):
        """
        Test that the Inform Shift Coordinator task is in the report for the
        patient when it's in progress
        """
        task_status = self.test_utils.get_report_triggered_action_status(
            self.act_summary)
        self.assertEqual(task_status, 'Task still in progress')

    def test_inform_shift_coordinator_task_on_report_completed(self):
        """
        Test that the Inform Shift Coordinator task is in the report for the
        patient when it's been completed
        """
        self.test_utils.complete_inform_shift_coordinator()
        task_status = self.test_utils.get_report_triggered_action_status(
            self.act_summary)
        self.assertTrue('Date: ' in task_status)

    def test_inform_shift_coordinator_task_after_shift_change(self):
        """
        Test that the Inform Shift Coordinator task is in task list of new
        nurses when a shift change happens
        """
        # TODO: Eckhard to clarify correct behaviour
        shift_change = self.test_utils.nursing_shift_change()
        nurse = shift_change.get('nurse')
        self.check_number_of_activities(1, user_id=nurse.id)

    def test_medical_team_task_created_on_complete(self):
        """
        Test that the Immediately Inform Medical team task is created when the
        Inform Shift Coordinator task is completed
        """
        activity_model = self.env['nh.activity']
        current_tasks = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.nurse.id]],
            ['data_model', '=', 'nh.clinical.notification.medical_team']
        ])
        self.test_utils.complete_inform_shift_coordinator()
        new_tasks = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.nurse.id]],
            ['data_model', '=', 'nh.clinical.notification.medical_team']
        ])
        self.assertEqual(len(new_tasks.ids), (len(current_tasks.ids) + 1))

    def test_mobile_api_complete_response(self):
        """
        Test the response from the Mobile API when cancelling the Call
        Ambulance notification
        """
        mobile_api = self.registry('nh.eobs.routes.slam')
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.nurse.id]],
            ['data_model', '=', self.data_model]
        ])
        result_json = mobile_api.complete_notification(
            self.env.cr,
            self.nurse.id,
            task.id
        )
        result = json.loads(result_json)
        self.assertEqual(
            result.get('description'),
            'All escalation tasks for <strong>{}</strong>'
            ' have been completed'.format(
                self.test_utils.patient.display_name
            )
        )
        self.assertEqual(result.get('title'), 'Submission successful')
        triggered_tasks = result.get('data', {}).get('related_tasks')
        self.assertEqual(len(triggered_tasks), 1)
        self.assertEqual(triggered_tasks[0].get('summary'),
                         'Urgently Inform Medical Team')
