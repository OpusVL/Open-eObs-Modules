from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from faker import Faker
import logging
from openerp.addons.nh_observations.tests.test_scenario import ActivityTypesTest

_logger = logging.getLogger(__name__)

faker = Faker()

"""
TESTS
we expect review ews frequency activity on every case except 1.
case 0 (score 0) -> no notifications
case 1 (score 1-4) -> we expect assess patient notification
case 2.1 (score 5-6) -> we expect urgently inform medical team and consider assessment by CCOT beep 6427 notifications
case 2.2 (three in one) -> we expect urgently inform medical team and consider assessment by CCOT beep 6427 notifications
case 3 (score 7+) -> we expect immediately inform medical team and urgent assessment by CCOT beep 6427 notifications

if we submit ews_data[PARAMETER][X] for every parameter in EWS we should obtain a score of X
except for special cases X = 18 and X = 19 which contain score 3 and 4 respectively but with three in one true.
"""


class TestBtuhPolicy(ActivityTypesTest):

    def setUp(self):
        global cr, uid, \
               register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, location_pool, pos_pool, user_pool, imd_pool, discharge_pool, \
               device_connect_pool, device_disconnect_pool, partner_pool, height_pool, blood_sugar_pool, \
               blood_product_pool, weight_pool, stools_pool, gcs_pool, vips_pool, o2target_pool, o2target_activity_pool

        cr, uid = self.cr, self.uid

        register_pool = self.registry('nh.clinical.adt.patient.register')
        patient_pool = self.registry('nh.clinical.patient')
        admit_pool = self.registry('nh.clinical.adt.patient.admit')
        discharge_pool = self.registry('nh.clinical.patient.discharge')
        activity_pool = self.registry('nh.activity')
        transfer_pool = self.registry('nh.clinical.adt.patient.transfer')
        ews_pool = self.registry('nh.clinical.patient.observation.ews')
        height_pool = self.registry('nh.clinical.patient.observation.height')
        weight_pool = self.registry('nh.clinical.patient.observation.weight')
        blood_sugar_pool = self.registry('nh.clinical.patient.observation.blood_sugar')
        blood_product_pool = self.registry('nh.clinical.patient.observation.blood_product')
        stools_pool = self.registry('nh.clinical.patient.observation.stools')
        gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
        vips_pool = self.registry('nh.clinical.patient.observation.vips')
        location_pool = self.registry('nh.clinical.location')
        pos_pool = self.registry('nh.clinical.pos')
        user_pool = self.registry('res.users')
        partner_pool = self.registry('res.partner')
        imd_pool = self.registry('ir.model.data')
        device_connect_pool = self.registry('nh.clinical.device.connect')
        device_disconnect_pool = self.registry('nh.clinical.device.disconnect')
        o2target_pool = self.registry('nh.clinical.o2level')
        o2target_activity_pool = self.registry('nh.clinical.patient.o2target')

        super(TestBtuhPolicy, self).setUp()
            
    def test_btuh_ews_observations_policy(self):
        ews_test_data = {
            'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,    3,    4,   20],
            'CASE':     [   0,    1,    1,    1,    1,    2,    2,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    2,    2,    3],
            'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
            'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   91,   91,   91,   91,   91,   91,   91,   99,   99,   91],
            'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
            'BT':       [37.5, 36.5, 36.5, 35.5, 35.5, 35.5, 38.0, 38.0, 38.0, 38.0, 38.0, 38.0, 38.0, 39.0, 39.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
            'BPS':      [ 110,  110,  110,  110,   90,   90,   90,   90,   80,   80,   80,   80,   80,   80,   75,  220,  220,  220,  120,  120,  220],
            'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
            'PR':       [  65,   55,   55,   55,   55,   90,   90,   90,   90,  110,  110,  110,  130,  130,   30,   30,  130,  130,   65,   65,  130],
            'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
        }
        
        o2_test_data = {
            'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,    8,    9,   10,   11,   12,   16,   17,    3,    4,   20],
            'CASE':     [   0,    1,    1,    1,    1,    2,    2,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    2,    2,    3],
            'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
            'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   92,   91,   90,   89,   88,   87,   87,   99,   99,   87],
            'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
            'BT':       [37.5, 36.5, 36.5, 35.5, 35.5, 35.5, 38.0, 38.0, 38.0, 38.0, 38.0, 38.0, 38.0, 39.0, 39.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
            'BPS':      [ 110,  110,  110,  110,   90,   90,   90,   90,   80,   80,   80,   80,   80,   80,   75,  220,  220,  220,  120,  120,  220],
            'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
            'PR':       [  65,   55,   55,   55,   55,   90,   90,   90,   90,  110,  110,  110,  130,  130,   30,   30,  130,  130,   65,   65,  130],
            'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
        }
        
        btuh_policy = {
            'frequencies': [720, 240, 60, 30],
            'risk': ['None', 'Low', 'Medium', 'High'],
            'notifications': [
                {'nurse': [], 'assessment': False, 'frequency': True},
                {'nurse': [], 'assessment': True, 'frequency': False},
                {'nurse': ['Urgently inform medical team', 'Consider assessment by CCOT beep 6427'], 'assessment': False, 'frequency': True},
                {'nurse': ['Immediately inform medical team', 'Urgent assessment by CCOT beep 6427'], 'assessment': False, 'frequency': True}
            ]
        }
        
        # environment
        pos1_env = self.create_pos_environment()
        # register
        [self.adt_patient_register(env=pos1_env) for i in range(5)]

        # admit
        [self.adt_patient_admit(data_vals={'other_identifier': other_identifier}, env=pos1_env) for other_identifier in pos1_env['other_identifiers']]

        # placements
        [self.patient_placement(data_vals={'patient_id': patient_id}, env=pos1_env) for patient_id in pos1_env['patient_ids']]

        # ews
        for i in range(0, 21):
            ews_id = self.observation_ews(data_vals={
                'respiration_rate': ews_test_data['RR'][i],
                'indirect_oxymetry_spo2': ews_test_data['O2'][i],
                'oxygen_administration_flag': ews_test_data['O2_flag'][i],
                'body_temperature': ews_test_data['BT'][i],
                'blood_pressure_systolic': ews_test_data['BPS'][i],
                'blood_pressure_diastolic': ews_test_data['BPD'][i],
                'pulse_rate': ews_test_data['PR'][i],
                'avpu_text': ews_test_data['AVPU'][i]
            }, env=pos1_env)

            frequency = btuh_policy['frequencies'][ews_test_data['CASE'][i]]
            clinical_risk = btuh_policy['risk'][ews_test_data['CASE'][i]]
            nurse_notifications = btuh_policy['notifications'][ews_test_data['CASE'][i]]['nurse']
            assessment = btuh_policy['notifications'][ews_test_data['CASE'][i]]['assessment']
            review_frequency = btuh_policy['notifications'][ews_test_data['CASE'][i]]['frequency']

            print "TEST - BTUH observation EWS: expecting score %s, frequency %s, risk %s" % (ews_test_data['SCORE'][i], frequency, clinical_risk)
            ews_activity = activity_pool.browse(cr, uid, ews_id)

            # # # # # # # # # # # # # # # # # # # # # # # # #
            # Check the score, frequency and clinical risk  #
            # # # # # # # # # # # # # # # # # # # # # # # # #
            self.assertEqual(ews_activity.data_ref.score, ews_test_data['SCORE'][i], msg='Score not matching')
            self.assertEqual(ews_activity.data_ref.clinical_risk, clinical_risk, msg='Risk not matching')
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', ews_pool._name)]
            ews_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(ews_activity_ids, msg='Next EWS activity was not triggered')
            next_ews_activity = activity_pool.browse(cr, uid, ews_activity_ids[0])
            self.assertEqual(next_ews_activity.data_ref.frequency, frequency, msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.assessment')]
            assessment_ids = activity_pool.search(cr, uid, domain)
            if assessment:
                self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
                activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 'nh.clinical.notification.frequency')]
                frequency_ids = activity_pool.search(cr, uid, domain)
                self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.nurse')]
            notification_ids = activity_pool.search(cr, uid, domain)
            self.assertEqual(len(notification_ids), len(nurse_notifications), msg='Wrong notifications triggered')
        
        # o2targets
        o2target_ids = o2target_pool.search(cr, uid, [('name', '=', '88-92')])
        [self.o2target(data_vals={'patient_id': patient_id, 'level_id': o2target_ids[0]}, env=pos1_env) for patient_id in pos1_env['patient_ids']]
        
        for i in range(0, 21):
            ews_id = self.observation_ews(data_vals={
                'respiration_rate': o2_test_data['RR'][i],
                'indirect_oxymetry_spo2': o2_test_data['O2'][i],
                'oxygen_administration_flag': o2_test_data['O2_flag'][i],
                'body_temperature': o2_test_data['BT'][i],
                'blood_pressure_systolic': o2_test_data['BPS'][i],
                'blood_pressure_diastolic': o2_test_data['BPD'][i],
                'pulse_rate': o2_test_data['PR'][i],
                'avpu_text': o2_test_data['AVPU'][i]
            }, env=pos1_env)

            frequency = btuh_policy['frequencies'][o2_test_data['CASE'][i]]
            clinical_risk = btuh_policy['risk'][o2_test_data['CASE'][i]]
            nurse_notifications = btuh_policy['notifications'][o2_test_data['CASE'][i]]['nurse']
            assessment = btuh_policy['notifications'][o2_test_data['CASE'][i]]['assessment']
            review_frequency = btuh_policy['notifications'][o2_test_data['CASE'][i]]['frequency']

            print "TEST - BTUH observation EWS: expecting score %s, frequency %s, risk %s" % (o2_test_data['SCORE'][i], frequency, clinical_risk)
            ews_activity = activity_pool.browse(cr, uid, ews_id)

            # # # # # # # # # # # # # # # # # # # # # # # # #
            # Check the score, frequency and clinical risk  #
            # # # # # # # # # # # # # # # # # # # # # # # # #
            self.assertEqual(ews_activity.data_ref.score, o2_test_data['SCORE'][i], msg='Score not matching')
            self.assertEqual(ews_activity.data_ref.clinical_risk, clinical_risk, msg='Risk not matching')
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', ews_pool._name)]
            ews_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(ews_activity_ids, msg='Next EWS activity was not triggered')
            next_ews_activity = activity_pool.browse(cr, uid, ews_activity_ids[0])
            self.assertEqual(next_ews_activity.data_ref.frequency, frequency, msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.assessment')]
            assessment_ids = activity_pool.search(cr, uid, domain)
            if assessment:
                self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
                activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 'nh.clinical.notification.frequency')]
                frequency_ids = activity_pool.search(cr, uid, domain)
                self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.nurse')]
            notification_ids = activity_pool.search(cr, uid, domain)
            if 88 <= o2_test_data['O2'][i] <= 92:
                self.assertEqual(len(notification_ids), len(nurse_notifications), msg='Wrong notifications triggered')
            else:
                # Review Oxygen Regime should be triggered as well
                self.assertEqual(len(notification_ids), len(nurse_notifications)+1, msg='Wrong notifications triggered')