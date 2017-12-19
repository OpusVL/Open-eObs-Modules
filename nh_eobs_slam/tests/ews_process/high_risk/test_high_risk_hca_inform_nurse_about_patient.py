import json

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestHighRiskHCAInformNurseAboutPatient(TransactionCase):
    """
    Test that the HCA and Nurse tasks are generated on a HCA submitting a high
    risk EWS observation
    """

    def setUp(self):
        super(TestHighRiskHCAInformNurseAboutPatient, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.hca = self.test_utils.hca
        self.test_utils.get_open_obs(user_id=self.hca.id)
        self.test_utils.complete_obs(
            clinical_risk_sample_data.HIGH_RISK_DATA,
            user_id=self.hca.id
        )
        self.data_model = 'nh.clinical.notification.hca'
        self.act_summary = 'Inform Nurse About Patient'

    def check_number_of_activities(self, expected_number, user_id=None):
        """
        Helper function to get list of activities and ensure correct number

        :param expected_number: Number of open activities we expect
        :param user_id: User to check for activities with
        """
        if not user_id:
            user_id = self.hca.id
        activities = self.test_utils.get_open_activities_for_patient(
            data_model=self.data_model,
            user_id=user_id
        )
        self.assertEqual(len(activities.ids), expected_number)

    def test_ews_nurse_task_create(self):
        """
        Test that the Nurse task associated with the Inform Nurse About Patient
        task is generated
        """
        activity = self.test_utils.get_open_activities_for_patient(
            data_model='nh.clinical.notification.nurse',
            user_id=self.test_utils.nurse.id
        )
        self.assertEqual(len(activity.ids), 1)

    def test_hca_task_created(self):
        """
        Test that the HCA's Inform Nurse About Patient task is generated
        """
        self.check_number_of_activities(1)

    def test_inform_shift_coordinator_task_created(self):
        """
        Test that the Inform Shift Coordinator task is generated at the same
        time
        """
        activity = self.test_utils.get_open_activities_for_patient(
            data_model='nh.clinical.notification.shift_coordinator',
            user_id=self.test_utils.nurse.id
        )
        self.assertEqual(len(activity.ids), 1)

    def test_hca_task_after_pme(self):
        """
        Test that the HCA's task is no longer available after PME
        """
        self.check_number_of_activities(1)
        self.test_utils.start_pme()
        # TODO: Eckhard to clarify if this should be 0 as EWS are cancelled on
        # PME
        self.check_number_of_activities(1)

    def test_hca_task_after_transfer_out(self):
        """
        Test that when transferring patient to another ward the user is no
        longer associated with the tasks
        """
        self.check_number_of_activities(1)
        self.test_utils.transfer_patient('WB')
        self.check_number_of_activities(0)

    def test_hca_task_after_transfer_in(self):
        """
        Test that when patient is transferred into ward that the escalation
        tasks are also transferred (current behaviour, would expect cancelled)
        """
        # TODO: Eckhard to clarify correct behaviour
        bed = self.test_utils.other_bed.id
        other_hca = self.test_utils.create_hca(bed)
        self.check_number_of_activities(1)
        self.test_utils.transfer_patient('WB')
        self.test_utils.place_patient(bed)
        self.check_number_of_activities(1, user_id=other_hca.id)

    def test_hca_task_after_partial(self):
        """
        Test that after a partial observation the HCA should still see the
        Inform Nurse About Patient task
        """
        self.check_number_of_activities(1)
        self.test_utils.get_open_obs(user_id=self.hca.id)
        self.test_utils.complete_obs(
            clinical_risk_sample_data.PARTIAL_DATA_ASLEEP,
            user_id=self.hca.id
        )
        self.check_number_of_activities(1)

    def test_hca_task_after_refusal(self):
        """
        Test that after a refused observation the HCA should still see the
        Inform Nurse About Patient task
        """
        self.check_number_of_activities(1)
        self.test_utils.get_open_obs(user_id=self.hca.id)
        self.test_utils.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA,
            user_id=self.hca.id
        )
        self.check_number_of_activities(1)

    def test_hca_task_on_workload_view(self):
        """
        Test that the Inform Nurse About Patient task is visible in the
        workload view on the desktop
        """
        workload_model = self.env['nh.activity.workload']
        workload = workload_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.hca.id]],
            ['date_scheduled', '!=', False],
            ['data_model', '=', self.data_model]
        ])
        self.assertEqual(len(workload.ids), 1)

    def test_hca_task_on_overdue_tasks_view(self):
        """
        Test that the Inform Nurse About Patient task is in the overdue tasks
        view when it's overdue
        """
        overdue_model = self.env['nh.clinical.overdue']
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.hca.id]],
            ['data_model', '=', self.data_model]
        ])
        overdue_task = overdue_model.browse(task.id)
        self.assertEqual(overdue_task.delay, 0)

    def test_hca_task_on_report_in_progress(self):
        """
        Test that the Inform Nurse About Patient task is in the report for the
        patient when it's in progress
        """
        task_status = self.test_utils.get_report_triggered_action_status(
            self.act_summary)
        self.assertEqual(task_status, 'Task still in progress')

    def test_hca_task_on_report_completed(self):
        """
        Test that the Inform Nurse About Patient task is in the report for the
        patient when it's been completed
        """
        self.test_utils.complete_open_activity(
            self.data_model, user_id=self.hca.id)
        task_status = self.test_utils.get_report_triggered_action_status(
            self.act_summary)
        self.assertTrue('Date: ' in task_status)

    def test_hca_task_after_shift_change(self):
        """
        Test that the Inform Nurse About Patient task is in task list of new
        HCA's when a shift change happens
        """
        # TODO: Eckhard to clarify correct behaviour
        shift_change = self.test_utils.nursing_shift_change()
        hca = shift_change.get('hca')
        self.check_number_of_activities(1, user_id=hca.id)

    def test_generates_no_tasks_on_complete(self):
        api_pool = self.registry('nh.eobs.api')
        activity_model = self.env['nh.activity']
        current_tasks = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['parent_id', '=', self.test_utils.spell_activity_id]
        ])
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.hca.id]],
            ['data_model', '=', self.data_model]
        ])
        api_pool.complete(
            self.env.cr,
            self.hca.id,
            task.id,
            {}
        )
        new_tasks = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['parent_id', '=', self.test_utils.spell_activity_id]
        ])
        self.assertEqual(len(new_tasks.ids), (len(current_tasks.ids) - 1))

    def test_mobile_api_complete_response(self):
        """
        Test the response from the Mobile API when cancelling the Call
        Ambulance notification
        """
        mobile_api = self.registry('nh.eobs.routes.slam')
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [self.hca.id]],
            ['data_model', '=', self.data_model]
        ])
        result_json = mobile_api.complete_notification(
            self.env.cr,
            self.hca.id,
            task.id
        )
        result = json.loads(result_json)
        self.assertEqual(
            result.get('description'),
            'The notification was successfully submitted'
        )
        self.assertEqual(result.get('title'), 'Submission successful')
        self.assertEqual(result.get('data', {}).get('related_tasks'), [])
