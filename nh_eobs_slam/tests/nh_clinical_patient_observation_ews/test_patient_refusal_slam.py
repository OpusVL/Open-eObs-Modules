# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs_slam.tests.nh_clinical_patient_observation_ews \
    .test_no_risk import TestNoClinicalRiskForPatientBetween4And7Days \
    as fourtoseven
from openerp.addons.nh_eobs_slam.tests.nh_clinical_patient_observation_ews \
    .test_no_risk import TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo \
    as sevenormore
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.addons.nh_observations import frequencies
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestPatientRefusalSlam(fourtoseven):

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.NO_RISK_DATA
        self.expected_score = 0
        self.expected_risk = 'None'
        self.expected_freq = \
            self.observation_pool.POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ
        super(TestPatientRefusalSlam, self).setUp()

        # Must use a nurse associated with the test patient's bed for actions
        # in these tests otherwise failures occur when getting patients for
        # activity.
        self.env.uid = self.user_id

        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        # nh.eobs.api not available to this module
        self.api_model = self.env['nh.clinical.api']

        self.datetime_test_utils = self.env['datetime_test_utils']
        self.test_utils_model = self.env['nh.clinical.test_utils']

    def test_refusal_with_no_clinical_risk_admitted_4_days_ago(self):
        """
        SLaM's policy is further customised to change the default no risk
        frequency from 12 hours to 24 hours when 4 days have passed since the
        patient's admission. This test checks that new observations have a
        frequency of 24 hours when the patient has been admitted 4 days or more
        ago.
        """
        obs_activity_before_refused = \
            self.ews_model.get_open_obs_activity(self.spell_id)
        obs_activity_after_refused = self.test_utils_model.refuse_open_obs(
            self.patient_id, self.spell_id)

        default_frequency = frequencies.ONE_DAY
        after_refused_frequency = frequencies\
            .PATIENT_REFUSAL_ADJUSTMENTS['None'][default_frequency][0]

        expected = datetime.strptime(obs_activity_before_refused
                                     .date_terminated, DTF) \
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )
        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)


class TestPatientRefusalSlamAfterSelectFrequency(sevenormore):
    """
    Test that the lower frequencies allowed by the select frequency task after
    seven days are probably adjusted after a patient refusal.
    """
    def setUp(self):
        super(TestPatientRefusalSlamAfterSelectFrequency, self).setUp()

        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        # nh.eobs.api not available to this module
        self.api_model = self.env['nh.clinical.api']

        self.datetime_test_utils = self.env['datetime_test_utils']
        self.test_utils_model = self.env['nh.clinical.test_utils']

        self.initial_no_risk_obs = \
            self.activity_model.browse(self.ews_activity_id)
        self.frequency_notification_activity = \
            self.activity_model.browse(self.triggered_ids[0])
        self.frequency_notification = \
            self.frequency_notification_activity.data_ref

    def test_refusal_with_no_clinical_risk_and_freq_one_week(self):
        """
        Test that a selected frequency of one week is properly adjusted after a
        patient refusal.
        """
        # Select a frequency
        self.frequency_notification.observation = \
            'nh.clinical.patient.observation.ews'
        self.frequency_notification.frequency = frequencies.EVERY_WEEK[0]
        self.frequency_notification.complete(
            self.frequency_notification_activity.id
        )

        obs_activity_before_refused = \
            self.ews_model.get_open_obs_activity(self.spell_id)
        obs_activity_after_refused = self.test_utils_model.refuse_open_obs(
            self.patient_id, self.spell_id
        )

        selected_frequency = self.frequency_notification.frequency
        after_refused_frequency = frequencies\
            .PATIENT_REFUSAL_ADJUSTMENTS['None'][selected_frequency][0]

        expected = \
            datetime.strptime(
                obs_activity_before_refused.date_terminated, DTF)\
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)
