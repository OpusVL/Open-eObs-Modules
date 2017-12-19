# coding: utf-8
""" Common Clinical Risk setUp"""
from datetime import datetime, timedelta
from unittest import SkipTest

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.addons.nh_eobs_mental_health.tests.common.observation \
    import ObservationCase


class ClinicalRiskCase(ObservationCase):

    def setUp(self):
        super(ClinicalRiskCase, self).setUp()
        if self.obs_data is None:
            message = "Tests should not be run from this class, only from " \
                      "subclasses. When running directly from this class " \
                      "there has not been any subclass to set `obs_data` " \
                      "and so the tests fail. This should be refactored in " \
                      "future so that this check is not necessary."
            self.skipTest(message)
        self.complete_obs(self.obs_data)

    def test_score(self):
        """ Test that the NEWS Score is correct """
        self.assertEqual(self.ews_activity.data_ref.score, self.expected_score,
                         msg='Score not matching')

    def test_clinical_risk(self):
        """ Test that the Clinical Risk is correct """
        self.assertEqual(self.ews_activity.data_ref.clinical_risk,
                         self.expected_risk,
                         msg='Risk not matching')

    def test_next_ews(self):
        """ Test that the next EWS is triggered """
        self.assertEqual(len(self.ews_activity_ids), 1,
                         msg='Next EWS activity was not triggered or '
                             'more than one triggered')

    def test_next_ews_freq(self):
        """ Test that the news EWS has the correct frequency """
        next_ews_activity = self.activity_pool.browse(self.cr, self.uid,
                                                      self.ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency,
                         self.expected_freq,
                         msg='Frequency not matching')

    def filter_notification_frequency_activities(self, ids, data_model):
        for triggered_activity_id in self.triggered_ids:
            triggered_activity = self.activity_pool.browse(
                self.cr, self.uid, triggered_activity_id)
            if triggered_activity.data_ref._name == data_model:
                return triggered_activity

    # TODO move somewhere this can be more easily reused.
    @classmethod
    def create_doctor_ward_and_bed(cls):
        cr, uid = cls.cr, cls.uid
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.spellboard_pool = cls.registry('nh.clinical.spellboard')
        cls.category_pool = cls.registry('res.partner.category')
        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.observation_pool = cls.registry(
            'nh.clinical.patient.observation.ews')

        cls.doctor_group = cls.group_pool.search(cr, uid, [
            ['name', '=', 'NH Clinical Doctor Group']
        ])[0]

        cls.doctor_category = cls.category_pool.search(cr, uid, [
            ['name', '=', 'Doctor']
        ])[0]

        cls.doctor = cls.user_pool.create(cr, uid, {
            'login': 'test_doctor',
            'password': 'test_doctor',
            'name': 'Test Doctor',
            'pos_id': 1,
            'pos_ids': [[6, 0, [1]]],
            'group_id': [[4, cls.doctor_group]],
            'category_id': [[4, cls.doctor_category]]
        })

        cls.ward = cls.location_pool.search(cr, uid, [
            ['code', '=', '325']
        ])[0]

        cls.bed = cls.location_pool.get_available_location_ids(cr, uid)[0]

    @classmethod
    def create_and_admit_patient_at_date(cls, hospital_number,
                                         admitted_days_ago,
                                         given_name='Jon', family_name='Snow'):
        cr, uid = cls.cr, cls.uid

        cls.patient_id = cls.api_pool.register(
            cr, cls.adt_id, hospital_number,
            {
                'given_name': given_name,
                'family_name': family_name,
                'patient_identifier': hospital_number
            })

        cls.patient = cls.patient_pool.search(cr, uid, [
            ['other_identifier', '=', hospital_number]
        ])[0]
        cls.patient_pool.write(cr, uid, cls.patient_id,
                               {'follower_ids': [(4, 1)]})

        cls.spell_id = cls.spellboard_pool.create(
            cr, cls.doctor, {
                'patient_id': cls.patient,
                'location_id': cls.ward,
                'code': hospital_number,
                'start_date': (
                    datetime.now() - timedelta(days=admitted_days_ago)
                ).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )

        placement_data = {
            'suggested_location_id': cls.ward,
            'patient_id': cls.patient
        }
        cls.placement_id = cls.placement_pool.create_activity(
            cr, cls.doctor, {}, placement_data)

        available_bed_ids = \
            cls.location_pool.get_available_location_ids(cr, uid)
        bed_ids = \
            [bed_id for bed_id in cls.bed_ids if bed_id in available_bed_ids]
        cls.bed_id = bed_ids[0]

        cls.activity_pool.submit(
            cr, cls.doctor, cls.placement_id, {'location_id': cls.bed_id})
        cls.activity_pool.complete(cr, cls.doctor, cls.placement_id)


class MedHighClinicalRiskCase(ClinicalRiskCase):

    def test_triggers_notifications(self):
        """ Test that the EWS observation didn't trigger any notifications"""
        self.assertEqual(len(self.triggered_ids), 1,
                         msg='Incorrect number of notifications '
                             'triggered - {0}'.format(len(self.triggered_ids)))

    def test_triggered_shiftc(self):
        """
        Test that the EWS observation triggered a shift coordinator
        notification
        """
        self.assertIn('nh.clinical.notification.shift_coordinator',
                      self.notifications,
                      msg="Wrong notification triggered")
