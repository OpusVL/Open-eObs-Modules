from openerp.tests import common
from openerp.osv.orm import except_orm
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.tools import config

import logging

_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()


class TestADTLDHPolicy(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestADTLDHPolicy, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.activity_pool = cls.registry('nh.activity')
        cls.user_pool = cls.registry('res.users')
        cls.group_pool = cls.registry('res.groups')
        cls.company_pool = cls.registry('res.company')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.api_pool = cls.registry('nh.eobs.api')

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})
        adt_group_ids = cls.group_pool.search(cr, uid, [['name', 'in', ['NH Clinical Admin Group', 'Contact Creation']]])
        cls.adt_id = cls.user_pool.create(cr, uid, {'name': 'Test ADT', 'login': 'testadt',
                                                    'groups_id': [[6, 0, adt_group_ids]], 'pos_id': cls.pos_id})
        cls.user_pool.write(cr, uid, uid, {'pos_id': cls.pos_id})
        eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])
        etl_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'etakelist']])
        cls.eobs_ward_id = cls.location_pool.create(cr, uid, {'name': 'Test eObs Ward', 'code': 'TESTWEOBS',
                                                              'usage': 'ward', 'parent_id': cls.hospital_id,
                                                              'context_ids': [[6, 0, eobs_context_id]]})
        cls.eobs_ward2_id = cls.location_pool.create(cr, uid, {'name': 'Test eObs Ward 2', 'code': 'TESTWEOBS2',
                                                               'usage': 'ward', 'parent_id': cls.hospital_id,
                                                               'context_ids': [[6, 0, eobs_context_id]]})
        cls.etl_ward_id = cls.location_pool.create(cr, uid, {'name': 'Test eTL Ward', 'code': 'TESTWETL',
                                                             'usage': 'ward', 'parent_id': cls.hospital_id,
                                                             'context_ids': [[6, 0, etl_context_id]]})

    def test_01_patient_register(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Register a Patient
        patient_id = self.api_pool.register(cr, uid, 'TEST000001', {})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', patient_id],
            ['data_model', 'in', ['nh.clinical.patient.tci', 'nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(triggered_ids, msg="A placement or TCI was triggered after Patient Register")

        self.api_pool.register(cr, uid, 'TEST000002', {})
        self.api_pool.register(cr, uid, 'TEST000003', {})
        self.api_pool.register(cr, uid, 'TEST000004', {})
        self.api_pool.register(cr, uid, 'TEST000005', {})

    def test_02_patient_update(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Update patient data
        self.api_pool.update(cr, uid, 'TEST000001', {'given_name': 'Perrin', 'family_name': 'Aybara'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci', 'nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(triggered_ids, msg="A placement or TCI was triggered after Patient Update")

    def test_03_patient_admit(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Admission patient not in the hospital -> eTL Location
        self.api_pool.admit(cr, uid, 'TEST000001', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was not triggered after eTL Location admission")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(triggered_ids, msg="Placement was triggered after eTL Location admission")

        # Scenario 2: Admission patient not in the hospital -> eObs Location
        self.api_pool.admit(cr, uid, 'TEST000002', {'location': 'TESTWEOBS'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="Placement was not triggered after eObs Location admission")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(triggered_ids, msg="TCI was triggered after eObs Location admission")

        # Patient 1 is in eTL, Patient 2 is in eObs, Patient 3 has no location (not admitted)
        # Scenario 3: Admission patient eTL Location -> eTL Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000001', {'location': 'TESTWETL'})

        # Scenario 4: Admission patient eTL Location -> eObs Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000001', {'location': 'TESTWEOBS'})

        # Scenario 5: Admission patient eObs Location -> eTL Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000002', {'location': 'TESTWETL'})

        # Scenario 6: Admission patient eObs Location -> eObs Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000002', {'location': 'TESTWEOBS'})

        # Scenario 7: Admission patient not in the hospital -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000003', {})

        # Scenario 8: Admission patient eTL Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000001', {})

        # Scenario 9: Admission patient eObs Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit(cr, uid, 'TEST000002', {})

    def test_04_spell_update(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Spell Update patient No Location -> eTL Location
        with self.assertRaises(except_orm):
            self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWETL'})
        self.api_pool.admit(cr, uid, 'TEST000004', {'location': 'TESTWETL'})

        # Scenario 2: Spell Update patient No Location -> eObs Location
        with self.assertRaises(except_orm):
            self.api_pool.admit_update(cr, uid, 'TEST000005', {'location': 'TESTWEOBS'})
        self.api_pool.admit(cr, uid, 'TEST000005', {'location': 'TESTWEOBS'})

        # Patient 4 is in eTL, Patient 5 is in eObs, Patient 3 has no location
        # Scenario 3: Spell Update patient eTL Location -> eTL Location
        tci_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(tci_ids[0], triggered_ids[0], msg="TCI triggered after eTL to eTL spell update")

        # Scenario 4: Spell Update patient eTL Location -> eObs Location
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWEOBS'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="Placement was not triggered after eTL to eObs Location spell update")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eTL to eObs Location spell update")

        # Scenario 5.1: Spell Update patient eObs Location -> eTL Location
        self.api_pool.admit_update(cr, uid, 'TEST000005', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000005'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was not triggered after eObs to eTL Location spell update")

        # Scenario 5.2: Spell Update patient eTL Location -> eObs Location -> eTL Location
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(tci_ids[0], triggered_ids[0], msg="TCI triggered after eTL to eObs to eTL spell update")
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWEOBS'})

        # Scenario 6: Spell Update patient eObs Location -> eObs Location
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWEOBS2'})
        placement_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(placement_ids, msg="Placement was not triggered after eObs Location spell update")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eObs Location spell update")
        self.api_pool.admit_update(cr, uid, 'TEST000004', {'location': 'TESTWEOBS2'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(triggered_ids[0], placement_ids[0], msg="Placement was triggered after eObs Location spell update to same ward")

        # Scenario 7: Spell Update patient No Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit_update(cr, uid, 'TEST000003', {'location': False})

        # Scenario 8: Spell Update patient eTL Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit_update(cr, uid, 'TEST000001', {'location': False})

        # Scenario 9: Spell Update patient eObs Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.admit_update(cr, uid, 'TEST000002', {'location': False})

    def test_05_cancel_admission(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Cancel Admission patient No Location
        with self.assertRaises(except_orm):
            self.api_pool.cancel_admit(cr, uid, 'TEST000003')

        # Scenario 2: Cancel Admission patient eTL Location
        self.api_pool.cancel_admit(cr, uid, 'TEST000005')
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000005'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="TCI was not cancelled after eTL Location cancel admission")

        # Scenario 3: Cancel Admission patient eObs Location
        self.api_pool.cancel_admit(cr, uid, 'TEST000004')
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000004'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="Placement was not cancelled after eObs Location cancel admission")

    def test_06_discharge(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Discharge patient No Location
        with self.assertRaises(except_orm):
            self.api_pool.discharge(cr, uid, 'TEST000003', {})

        # Scenario 2: Discharge patient eTL Location
        self.api_pool.discharge(cr, uid, 'TEST000001', {})
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.spell']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="Spell was not completed after eTL Location discharge")
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="TCI was not cancelled after eTL Location discharge")

        # Scenario 3: Discharge patient eObs Location
        self.api_pool.discharge(cr, uid, 'TEST000002', {})
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.spell']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertFalse(activity_ids, msg="Spell was not completed after eObs Location discharge")

    def test_07_cancel_discharge(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Cancel Discharge patient No Location
        with self.assertRaises(except_orm):
            self.api_pool.cancel_discharge(cr, uid, 'TEST000003')

        # Scenario 2: Cancel Discharge patient eTL Location
        self.api_pool.cancel_discharge(cr, uid, 'TEST000001')
        spell_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.spell']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(spell_ids, msg="Spell was not reopened after eTL Location discharge")
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']],
            ['parent_id', 'in', spell_ids]])
        self.assertTrue(activity_ids, msg="TCI activity not found after eTL Location cancel discharge")

        # Scenario 3: Cancel Discharge patient eObs Location
        self.api_pool.cancel_discharge(cr, uid, 'TEST000002')
        spell_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.spell']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(spell_ids, msg="Spell was not reopened after eObs Location discharge")
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(activity_ids, msg="Placement activity not found after eObs Location cancel discharge")

    def test_08_transfer(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Transfer patient No Location -> eTL Location
        with self.assertRaises(except_orm):
            self.api_pool.transfer(cr, uid, 'TEST000003', {'location': 'TESTWETL'})

        # Scenario 2: Transfer patient No Location -> eObs Location
        with self.assertRaises(except_orm):
            self.api_pool.transfer(cr, uid, 'TEST000003', {'location': 'TESTWEOBS'})

        # Patient 1 is in eTL, Patient 2 is in eObs, Patient 3 has no location
        # Scenario 3: Transfer patient eTL Location -> eTL Location
        tci_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(tci_ids[0], triggered_ids[0], msg="TCI triggered after eTL to eTL transfer")

        # Scenario 4: Transfer patient eTL Location -> eObs Location
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWEOBS'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="Placement was not triggered after eTL to eObs Location transfer")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eTL to eObs Location transfer")

        # Scenario 5.1: Transfer patient eObs Location -> eTL Location
        self.api_pool.transfer(cr, uid, 'TEST000002', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was not triggered after eObs to eTL Location transfer")

        # Scenario 5.2: Transfer patient eTL Location -> eObs Location -> eTL Location
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWETL'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(tci_ids[0], triggered_ids[0], msg="TCI triggered after eTL to eObs to eTL transfer")
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWEOBS'})

        # Scenario 6: Transfer patient eObs Location -> eObs Location
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWEOBS2'})
        placement_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(placement_ids, msg="Placement was not triggered after eObs Location transfer")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eObs Location transfer")
        self.api_pool.transfer(cr, uid, 'TEST000001', {'location': 'TESTWEOBS2'})
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(triggered_ids[0], placement_ids[0], msg="Placement was triggered after eObs Location transfer to same ward")

        # Scenario 7: Transfer patient No Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.transfer(cr, uid, 'TEST000003', {'location': False})

        # Scenario 8: Transfer patient eTL Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.transfer(cr, uid, 'TEST000002', {'location': False})

        # Scenario 9: Transfer patient eObs Location -> No Location
        with self.assertRaises(except_orm):
            self.api_pool.transfer(cr, uid, 'TEST000001', {'location': False})

    def test_09_cancel_transfer(self):
        cr, uid = self.cr, self.uid

        # Patient 1 is in eObs, Patient 2 is in eTL, Patient 3 has no location
        # Scenario 1: Cancel Transfer patient eTL Location -> eTL Location
        self.api_pool.transfer(cr, uid, 'TEST000002', {'location': 'TESTWETL'})
        tci_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.api_pool.cancel_transfer(cr, uid, 'TEST000002')
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(tci_ids[0], triggered_ids[0], msg="TCI triggered after eTL to eTL cancel transfer")

        # Scenario 2: Cancel Transfer patient eTL Location -> eObs Location
        self.api_pool.cancel_transfer(cr, uid, 'TEST000002')
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="Placement was not triggered after eTL to eObs Location cancel transfer")
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000002'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eTL to eObs Location cancel transfer")

        # Scenario 3: Transfer patient eObs Location -> eObs Location
        placement_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.api_pool.cancel_transfer(cr, uid, 'TEST000001')
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEqual(triggered_ids[0], placement_ids[0], msg="Placement was triggered after eObs Location cancel transfer to same ward")
        self.api_pool.cancel_transfer(cr, uid, 'TEST000001')
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.placement']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertNotEqual(triggered_ids[0], placement_ids[0], msg="Placement was not triggered after eObs Location cancel transfer")

        # Scenario 4: Cancel Transfer patient eObs Location -> eTL Location
        self.api_pool.cancel_transfer(cr, uid, 'TEST000001')
        triggered_ids = self.activity_pool.search(cr, uid, [
            ['patient_id.other_identifier', '=', 'TEST000001'],
            ['data_model', 'in', ['nh.clinical.patient.tci']],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertTrue(triggered_ids, msg="TCI was cancelled after eObs to eTL Location cancel transfer")