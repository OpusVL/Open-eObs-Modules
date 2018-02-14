from openerp.tests import common
from openerp.osv.orm import except_orm
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.tools import config

import logging

_logger = logging.getLogger(__name__)


class TestNEWSListerPolicy(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestNEWSListerPolicy, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.activity_pool = cls.registry('nh.activity')
        cls.user_pool = cls.registry('res.users')
        cls.group_pool = cls.registry('res.groups')
        cls.company_pool = cls.registry('res.company')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')
        cls.api_pool = cls.registry('nh.eobs.api')
        cls.o2level_pool = cls.registry('nh.clinical.o2level')
        cls.o2target_pool = cls.registry('nh.clinical.patient.o2target')
        cls.ps_pool = cls.registry('nh.clinical.patient.post_surgery')
        cls.cc_pool = cls.registry('nh.clinical.patient.critical_care')
        cls.pc_pool = cls.registry('nh.clinical.patient.palliative_care')

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})
        adt_group_ids = cls.group_pool.search(cr, uid, [['name', 'in', ['NH Clinical Admin Group', 'Contact Creation']]])
        nurse_group_ids = cls.group_pool.search(cr, uid, [['name', 'in', ['NH Clinical Nurse Group']]])
        cls.adt_id = cls.user_pool.create(cr, uid, {'name': 'Test ADT', 'login': 'testadt',
                                                    'groups_id': [[4, group_id] for group_id in adt_group_ids],
                                                    'pos_id': cls.pos_id})
        cls.user_pool.write(cr, uid, uid, {'pos_id': cls.pos_id})
        context_ids = cls.context_pool.search(cr, uid, [['name', 'in', ['eobs', 'renal']]])
        cls.eobs_ward_id = cls.location_pool.create(cr, uid, {'name': 'Test eObs Ward', 'code': 'TESTWEOBS',
                                                              'usage': 'ward', 'parent_id': cls.hospital_id,
                                                              'context_ids': [[6, 0, context_ids]]})
        cls.bed_ids = [cls.location_pool.create(cr, uid, {'name': 'Bed %s' % i, 'code': 'TESTB%s' % i,
                                                          'usage': 'bed', 'parent_id': cls.eobs_ward_id,
                                                          'context_ids': [[6, 0, context_ids]]}) for i in range(10)]
        cls.nurse_id = cls.user_pool.create(cr, uid, {'name': 'Test Nurse', 'login': 'testnurse',
                                                      'groups_id': [[4, group_id] for group_id in nurse_group_ids],
                                                      'pos_id': cls.pos_id, 'location_ids': [[6, 0, cls.bed_ids]]})
        cls.patient_id = cls.api_pool.register(cr, cls.adt_id, 'TESTHN001', {})
        cls.api_pool.admit(cr, cls.adt_id, 'TESTHN001', {'location': 'TESTWEOBS'})
        cls.spell_id = cls.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                                                          ['patient_id', '=', cls.patient_id]])[0]
        placement_id = cls.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.placement'],
                                                          ['patient_id', '=', cls.patient_id],
                                                          ['state', '=', 'scheduled']])
        cls.activity_pool.submit(cr, uid, placement_id[0], {'location_id': cls.bed_ids[0]})
        cls.activity_pool.complete(cr, uid, placement_id[0])

    def test_01_lister_ews_policy_no_risk(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation 0 Score without O2 Target

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 0,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 0, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'None', msg='Risk not matching')
        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 480, msg='Frequency not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertFalse(triggered_ids, msg='Notification triggered')

    def test_02_lister_ews_policy_low_risk(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation Low Risk without O2 Target

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 11,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 0,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 1, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'Low', msg='Risk not matching')
        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 240, msg='Frequency not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 1, msg='No triggers or more than 1 notification triggered')
        activity = self.activity_pool.browse(cr, uid, triggered_ids[0])
        self.assertEqual(activity.data_model, 'nh.clinical.notification.assessment', msg="Wrong notification triggered")

        self.api_pool.complete(cr, self.nurse_id, triggered_ids[0], {})
        domain = [
            ('creator_id', '=', triggered_ids[0]),
            ('state', 'not in', ['completed', 'cancelled'])]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 1, msg='No triggers or more than 1 notification triggered')
        activity = self.activity_pool.browse(cr, uid, triggered_ids[0])
        self.assertEqual(activity.data_model, 'nh.clinical.notification.frequency', msg="Wrong notification triggered")

    def test_03_lister_ews_policy_medium_risk(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation Medium Risk without O2 Target

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 11,
            'indirect_oxymetry_spo2': 95,
            'oxygen_administration_flag': 0,
            'body_temperature': 36.0,
            'blood_pressure_systolic': 110,
            'blood_pressure_diastolic': 70,
            'pulse_rate': 50,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 5, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'Medium', msg='Risk not matching')
        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 60, msg='Frequency not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 1, msg='No triggers or more than 1 notification triggered')
        activity = self.activity_pool.browse(cr, uid, triggered_ids[0])
        self.assertEqual(activity.data_model, 'nh.clinical.notification.assessment', msg="Wrong notification triggered")

        self.api_pool.complete(cr, self.nurse_id, triggered_ids[0], {})
        domain = [
            ('creator_id', '=', triggered_ids[0]),
            ('state', 'not in', ['completed', 'cancelled'])]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 3, msg='Incorrect number of notifications triggered')
        activities = self.activity_pool.browse(cr, uid, triggered_ids)
        models = ['nh.clinical.notification.nurse', 'nh.clinical.notification.frequency',
                  'nh.clinical.notification.inform_doctor']
        self.assertTrue(activities[0].data_model in models, msg="Wrong notification triggered")
        self.assertTrue(activities[1].data_model in models, msg="Wrong notification triggered")
        self.assertTrue(activities[2].data_model in models, msg="Wrong notification triggered")

    def test_04_lister_ews_policy_high_risk(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation High Risk without O2 Target

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 24,
            'indirect_oxymetry_spo2': 93,
            'oxygen_administration_flag': 0,
            'body_temperature': 38.5,
            'blood_pressure_systolic': 110,
            'blood_pressure_diastolic': 70,
            'pulse_rate': 50,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 7, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'High', msg='Risk not matching')
        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 15, msg='Frequency not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 1, msg='No triggers or more than 1 notification triggered')
        activity = self.activity_pool.browse(cr, uid, triggered_ids[0])
        self.assertEqual(activity.data_model, 'nh.clinical.notification.assessment', msg="Wrong notification triggered")

        self.api_pool.complete(cr, self.nurse_id, triggered_ids[0], {})
        domain = [
            ('creator_id', '=', triggered_ids[0]),
            ('state', 'not in', ['completed', 'cancelled'])]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 2, msg='Incorrect number of notifications triggered')
        activities = self.activity_pool.browse(cr, uid, triggered_ids)
        models = ['nh.clinical.notification.nurse', 'nh.clinical.notification.inform_doctor']
        self.assertTrue(activities[0].data_model in models, msg="Wrong notification triggered")
        self.assertTrue(activities[1].data_model in models, msg="Wrong notification triggered")

    def test_05_lister_ews_policy_o2_target(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation Score bigger O2 Target Range

        o2level_id = self.o2level_pool.create(cr, uid, {'min': 88, 'max': 95})
        o2target_id = self.o2target_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                         {'level_id': o2level_id, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, o2target_id)

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 11,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 1,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 3, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'Low', msg='Risk not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 1, msg='No triggers or more than 1 notification triggered')
        activity = self.activity_pool.browse(cr, uid, triggered_ids[0])
        self.assertEqual(activity.data_model, 'nh.clinical.notification.assessment', msg="Wrong notification triggered")

        # Scenario 2: Submit a NEWS Observation Score within O2 Target Range

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 88,
            'oxygen_administration_flag': 1,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.score, 5, msg='Score not matching')
        self.assertEqual(ews_activity.data_ref.clinical_risk, 'Medium', msg='Risk not matching')

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')]
        triggered_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(triggered_ids), 0, msg='Notifications triggered')

        o2target_id = self.o2target_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                         {'level_id': False, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, o2target_id)

    def test_06_lister_ews_policy_post_surgery(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Activate Post Surgery Special circumstance

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 0,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]
        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.frequency, 480, msg='Frequency not matching')

        ps_id = self.ps_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                      {'status': True, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, ps_id)

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]
        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.frequency, 60, msg='Frequency not matching')

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 60, msg='Frequency not matching')

        ps_id = self.ps_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                      {'status': False, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, ps_id)

    def test_07_lister_ews_policy_critical_care(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Activate Critical Care Special circumstance

        cc_id = self.cc_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                      {'status': True, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, cc_id)

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)
        self.assertEqual(ews_activity.data_ref.frequency, 60, msg='Frequency not matching')

        data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 0,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        domain = [
            ('creator_id', '=', ews_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)]
        ews_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(ews_activity_ids), 1, msg='Next EWS activity was not triggered or more than one triggered')
        next_ews_activity = self.activity_pool.browse(cr, uid, ews_activity_ids[0])
        self.assertEqual(next_ews_activity.data_ref.frequency, 240, msg='Frequency not matching')

        cc_id = self.cc_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                      {'status': False, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, cc_id)

    def test_08_lister_height_and_weight_triggered(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Make sure there is a weight observation and height observation for the patient

        activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.weight'],
                                                          ['patient_id', '=', self.patient_id],
                                                          ['state', '=', 'scheduled']])
        self.assertTrue(activity_id, msg="No weight observation triggered after placement")
        activity = self.activity_pool.browse(cr, uid, activity_id)
        self.assertGreater((dt.now()+td(hours=1)).strftime(dtf), activity.date_scheduled)

        activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.height'],
                                                          ['patient_id', '=', self.patient_id],
                                                          ['state', '=', 'scheduled']])
        self.assertTrue(activity_id, msg="No height observation triggered after placement")
        activity = self.activity_pool.browse(cr, uid, activity_id)
        self.assertGreater((dt.now()+td(hours=1)).strftime(dtf), activity.date_scheduled)

    def test_09_lister_ews_vpu_triggers_blood_sugar(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Submit a NEWS Observation with VPU

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 24,
            'indirect_oxymetry_spo2': 93,
            'oxygen_administration_flag': 0,
            'body_temperature': 38.5,
            'blood_pressure_systolic': 110,
            'blood_pressure_diastolic': 70,
            'pulse_rate': 50,
            'avpu_text': 'V'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)

        domain = [
            ('creator_id', '=', ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', 'nh.clinical.patient.observation.blood_sugar')]
        bs_activity_ids = self.activity_pool.search(cr, uid, domain)
        self.assertEqual(len(bs_activity_ids), 1, msg='Blood Sugar activity was not triggered or more than one triggered')

    def test_10_lister_ews_policy_palliative_care(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Activate Palliative Care Special circumstance

        pc_id = self.pc_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                      {'status': True, 'patient_id': self.patient_id})
        self.activity_pool.complete(cr, uid, pc_id)

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])
        self.assertFalse(ews_activity_id, msg="NEWS activities not cancelled")

        activity_ids = self.activity_pool.search(cr, uid, [['data_model', 'ilike', '%notification%'],
                                                           ['patient_id', '=', self.patient_id],
                                                           ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="Notifications not cancelled")