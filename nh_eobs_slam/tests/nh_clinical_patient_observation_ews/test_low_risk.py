# coding: utf-8
""" Test low Clinical Risk """
from openerp.addons.nh_eobs_slam.tests.common \
    .clinical_risk_common import ClinicalRiskCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestLowClinicalRisk(ClinicalRiskCase):
    """
    Test that observations with low clinical risk work properly
    """

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.LOW_RISK_DATA
        self.expected_score = 1
        self.expected_risk = 'Low'
        self.expected_freq = 360
        super(TestLowClinicalRisk, self).setUp()

    def test_triggers_notifications(self):
        """ Test that the EWS observation didn't trigger any notifications"""
        self.assertEqual(len(self.triggered_ids), 1,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))

    def test_triggered_assessment(self):
        """ Test that the EWS observation triggered an assessment """
        activity = self.activity_pool.browse(self.cr, self.uid,
                                             self.triggered_ids[0])
        self.assertEqual(activity.data_model,
                         'nh.clinical.notification.assessment',
                         msg="Wrong notification triggered")


class TestLowClinicalRiskPatientAdmittedLessThanSevenDaysAgo(ClinicalRiskCase):
    """
    Test observations of patients admitted less than seven days ago.
    """

    @classmethod
    def setUpClass(cls):
        super(TestLowClinicalRiskPatientAdmittedLessThanSevenDaysAgo, cls)\
            .setUpClass()

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_LESS_THAN_7_DAYS_AGO', 6
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.LOW_RISK_DATA
        self.expected_score = 1
        self.expected_risk = 'Low'
        self.expected_freq = 360
        super(TestLowClinicalRiskPatientAdmittedLessThanSevenDaysAgo, self)\
            .setUp()

    def test_one_notifications_for_patient_admitted_less_than_seven_days(self):
        """
        Test that the EWS observation triggered the correct number of
        notifications when the patient has been admitted for less than 7 days.
        """
        self.assertEqual(len(self.triggered_ids), 1,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))

    def test_triggered_assessment(self):
        """ Test that the EWS observation triggered an assessment """
        activity = self.activity_pool.browse(self.cr, self.uid,
                                             self.triggered_ids[0])
        self.assertEqual(activity.data_model,
                         'nh.clinical.notification.assessment',
                         msg="Wrong notification triggered")


class TestLowClinicalRiskPatientAdmittedSevenOrMoreDaysAgo(ClinicalRiskCase):
    """
    Test observations of patients admitted seven or more days ago.
    """

    @classmethod
    def setUpClass(cls):
        super(TestLowClinicalRiskPatientAdmittedSevenOrMoreDaysAgo, cls)\
            .setUpClass()

        cls.create_doctor_ward_and_bed()
        cls.create_and_admit_patient_at_date(
            'I_WAS_ADMITTED_MORE_THAN_7_DAYS_AGO', 8
        )

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.LOW_RISK_DATA
        self.expected_score = 1
        self.expected_risk = 'Low'
        self.expected_freq = 360
        super(TestLowClinicalRiskPatientAdmittedSevenOrMoreDaysAgo, self)\
            .setUp()

    def test_one_notifications_for_patient_admitted_seven_plus_days_ago(self):
        """
        Test that the EWS observation triggered the correct number of
        notifications when the patient has been admitted for 7 days or more.
        """
        self.assertEqual(len(self.triggered_ids), 1,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))

    def test_triggered_assessment(self):
        """ Test that the EWS observation triggered an assessment """
        activity = self.activity_pool.browse(self.cr, self.uid,
                                             self.triggered_ids[0])
        self.assertEqual(activity.data_model,
                         'nh.clinical.notification.assessment',
                         msg="Wrong notification triggered")
