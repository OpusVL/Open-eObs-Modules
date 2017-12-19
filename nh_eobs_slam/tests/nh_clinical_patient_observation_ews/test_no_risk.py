# coding: utf-8
""" Test No Clinical Risk """
from openerp.addons.nh_eobs_slam.tests.common\
    .clinical_risk_common import ClinicalRiskCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.addons.nh_observations import frequencies


class TestNoClinicalRiskForPatientBetween4And7Days(ClinicalRiskCase):
    """
    Test observation and triggered tasks for patients admitted between four
    and seven days ago.
    """

    @classmethod
    def setUpClass(cls):
        super(TestNoClinicalRiskForPatientBetween4And7Days, cls) \
            .setUpClass()

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_BETWEEN_4_AND_7_DAYS_AGO', 6
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.NO_RISK_DATA
        self.expected_score = 0
        self.expected_risk = 'None'
        self.expected_freq = \
            self.observation_pool.POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ
        super(TestNoClinicalRiskForPatientBetween4And7Days, self) \
            .setUp()

    def test_no_notifications_for_patient_admitted_4_7_days_ago(self):
        """
        Test that the EWS observation triggered the correct number of
        notifications when the patient has been admitted between 4 and 7 days.
        """
        self.assertEqual(len(self.triggered_ids), 0,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))


class TestNoClinicalRiskPatientAdmittedLessThanFourDaysAgo(ClinicalRiskCase):
    """
    Test observations of patients admitted less than Four days ago.
    """

    @classmethod
    def setUpClass(cls):
        super(TestNoClinicalRiskPatientAdmittedLessThanFourDaysAgo, cls)\
            .setUpClass()

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_LESS_THAN_4_DAYS_AGO', 3
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.NO_RISK_DATA
        self.expected_score = 0
        self.expected_risk = 'None'
        self.expected_freq = \
            self.observation_pool.PRE_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ
        super(TestNoClinicalRiskPatientAdmittedLessThanFourDaysAgo, self)\
            .setUp()

    def test_no_notifications_for_patient_admitted_less_than_four_days(self):
        """
        Test that the EWS observation triggered the correct number of
        notifications when the patient has been admitted for less than 7 days.
        """
        self.assertEqual(len(self.triggered_ids), 0,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))


class TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo(ClinicalRiskCase):
    """
    Test observations of patients admitted seven or more days ago.
    """

    @classmethod
    def setUpClass(cls):
        super(TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo, cls)\
            .setUpClass()

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_MORE_THAN_7_DAYS_AGO', 8
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.NO_RISK_DATA
        self.expected_score = 0
        self.expected_risk = 'None'
        self.expected_freq = \
            self.observation_pool.POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ
        super(TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo, self)\
            .setUp()

    def test_one_notification_for_patient_admitted_seven_plus_days_ago(self):
        """
        Test that the EWS observation triggered the correct number of
        notifications when the patient has been admitted for 7 days or more.
        """
        self.assertEqual(len(self.triggered_ids), 1,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))

    def test_select_frequency_notification_for_pt_admitted_7_plus_days(self):
        """
        Test that the EWS observation triggered a 'Select Frequency'
        notification when the patient has been admitted for 7 days or more.
        """
        for triggered_activity_id in self.triggered_ids:
            triggered_activity = self.activity_pool.browse(
                self.cr, self.uid, triggered_activity_id)
            if triggered_activity.data_ref._name == \
                    'nh.clinical.notification.select_frequency':
                return
        raise AssertionError("No 'Select Frequency' notification was "
                             "triggered by the observation")

    def test_select_frequency_notification_available_frequencies(self):
        """
        Test that the frequencies available for selection from the
        'Select Frequency' notification are correct.
        """
        # TODO Frequency for the patient is not changed until
        # get_form_description() is called. This could be bad.
        notification_pool = \
            self.registry('nh.clinical.notification.select_frequency')

        for triggered_activity_id in self.triggered_ids:
            triggered_activity = self.activity_pool.browse(
                self.cr, self.uid, triggered_activity_id)
            notification = triggered_activity.data_ref
            notification_pool.get_form_description(
                self.cr, self.uid, notification.id, self.patient_id)
            if notification._name == \
                    'nh.clinical.notification.select_frequency':
                actual_frequencies = [
                    field for field in notification._form_description
                    if field['name'] == 'frequency'][0]['selection']
                observation_pool = \
                    self.registry('nh.clinical.notification.select_frequency')
                expected_frequencies = observation_pool._NO_RISK_FREQUENCIES
                self.assertEquals(actual_frequencies, expected_frequencies)
                return
        raise AssertionError("No 'Select Frequency' notification was "
                             "triggered by the observation")

    def test_weekly_frequency_agreed_notif_after_select_weekly_frequency(self):
        """ Test that when a nurse selects a frequency of 'weekly' for a low
        risk patient that a notification is triggered to confirm that this was
        agreed with the medical team.
        """
        select_frequency_notification_activity = self.activity_pool.browse(
            self.cr, self.uid, self.triggered_ids[0])
        select_frequency_notification = \
            select_frequency_notification_activity.data_ref

        select_frequency_notification.frequency = frequencies.EVERY_WEEK[0]

        frequency_pool = \
            self.registry('nh.clinical.notification.select_frequency')
        frequency_pool.complete(
            self.cr, self.uid, self.triggered_ids[0])

        domain = [
            ('patient_id', '=', self.patient_id),
            ('data_model', '=',
             'nh.clinical.notification.weekly_frequency_agreed'),
            ('state', 'not in', ['completed', 'cancelled']),
            ('creator_id', '=', [self.triggered_ids[0]])
        ]
        weekly_frequency_agreed_notification_id = self.activity_pool.search(
            self.cr, self.uid, domain)

        if len(weekly_frequency_agreed_notification_id) == 0:
            raise AssertionError(
                "No 'weekly frequency agreed' notification triggered by "
                "completion of weekly 'select frequency' notification.")

    def test_no_weekly_frequency_agreed_notif_after_non_weekly_frequency(self):
        """ Test that when a nurse selects a frequency of 'weekly' for a low
        risk patient that a notification is triggered to confirm that this was
        agreed with the medical team.
        """
        select_frequency_notification_activity = self.activity_pool.browse(
            self.cr, self.uid, self.triggered_ids[0])
        select_frequency_notification = \
            select_frequency_notification_activity.data_ref

        select_frequency_notification.frequency = frequencies.EVERY_DAY[0]

        frequency_pool = \
            self.registry('nh.clinical.notification.select_frequency')
        frequency_pool.complete(
            self.cr, self.uid, self.triggered_ids[0])

        domain = [
            ('patient_id', '=', self.patient_id),
            ('data_model', '=',
             'nh.clinical.notification.weekly_frequency_agreed'),
            ('state', 'not in', ['completed', 'cancelled']),
            ('creator_id', '=', [self.triggered_ids[0]])
        ]
        weekly_frequency_agreed_notification_id = self.activity_pool.search(
            self.cr, self.uid, domain)

        if len(weekly_frequency_agreed_notification_id) > 0:
            raise AssertionError(
                "A 'weekly frequency agreed' notification was triggered by "
                "completion of daily 'select frequency' notification.")


class TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgoHca(ClinicalRiskCase):

    @classmethod
    def setUpClass(cls):
        super(TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgoHca, cls)\
            .setUpClass()
        cr, uid = cls.cr, cls.uid

        # Change user_id from a nurse to a HCA.
        hca_group_ids = cls.group_pool.search(
            cr, uid, [('name', 'in', ['NH Clinical HCA Group'])])
        cls.user_id = cls.user_pool.create(
            cr, uid, {
                'name': 'Test HCA',
                'login': 'testhca',
                'groups_id': [[4, group_id] for group_id in hca_group_ids],
                'pos_id': cls.pos_id,
                'location_ids': [[6, 0, cls.bed_ids]]
            }
        )

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_MORE_THAN_7_DAYS_AGO', 8
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.NO_RISK_DATA
        self.expected_score = 0
        self.expected_risk = 'None'
        self.expected_freq = \
            self.observation_pool.POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ
        super(TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgoHca, self)\
            .setUp()

    def test_select_frequency_notif_for_patient_admitted_week_plus_ago(self):
        """
        Test that the EWS observation triggered a 'Select Frequency'
        notification when the patient has been admitted for 7 days or more.
        """
        data_model = 'nh.clinical.notification.select_frequency'
        select_frequency = super(
            TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgoHca, self). \
            filter_notification_frequency_activities(self.triggered_ids,
                                                     data_model)
        if select_frequency is None:
            raise AssertionError("No 'Select Frequency' notification was "
                                 "triggered by the observation")

    def test_review_frequency_notification_not_visible_to_hca(self):
        """
        Test that HCA's do not have access to review frequency notifications
        triggered by EWS observations that the have confucted.

        :return:
        """
        data_model = 'nh.clinical.notification.select_frequency'
        select_frequency = super(
            TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgoHca, self). \
            filter_notification_frequency_activities(self.triggered_ids,
                                                     data_model)
        hca_has_access = self.api_pool.check_activity_access(
            self.cr, self.user_id, select_frequency.id)
        self.assertFalse(hca_has_access)
