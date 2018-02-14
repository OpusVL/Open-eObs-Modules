# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.osv import osv
from openerp.tests.common import TransactionCase
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import base64
import os.path


mocked_print_called = 0


class SettingsPoolMockBrowse(object):

    def __init__(self):
        self.locations_to_print = []


class TestNHClinicalBackupProcedure(TransactionCase):

    def setUp(self):
        super(TestNHClinicalBackupProcedure, self).setUp()
        cr, uid = self.cr, self.uid

        self.users_pool = self.registry('res.users')
        self.activity_pool = self.registry('nh.activity')
        self.location_pool = self.registry('nh.clinical.location')
        self.pos_pool = self.registry('nh.clinical.pos')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.apidemo = self.registry('nh.clinical.api.demo')
        self.api_pool = self.registry('nh.eobs.api')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')
        self.activity_pool = self.registry('nh.activity')
        self.context_pool = self.registry('nh.clinical.context')
        self.placement_pool = self.registry('nh.clinical.patient.placement')
        self.mrsa_pool = self.registry('nh.clinical.patient.mrsa')
        self.diabetes_pool = self.registry('nh.clinical.patient.diabetes')
        self.ir_pool = self.registry('ir.attachment')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.patient_ids = self.apidemo.build_unit_test_env1(
            cr, uid, bed_count=4, patient_count=4)
        self.wu_id = self.location_pool.search(
            cr, uid, [('code', '=', 'U')])[0]
        self.wt_id = self.location_pool.search(
            cr, uid, [('code', '=', 'T')])[0]
        self.location_pool.write(
            cr, uid, self.wu_id, {'backup_observations': True})
        self.pos_id = self.location_pool.read(
            cr, uid, self.wu_id, ['pos_id'])['pos_id'][0]
        self.bed_ids = self.location_pool.read(
            cr, uid, self.wu_id, ['child_ids'])['child_ids']
        self.bed_id = self.bed_ids[0]
        self.bed_id1 = self.bed_ids[1]
        self.bed_id2 = self.bed_ids[2]

        self.patient_id = self.patient_ids[0]
        self.patient_pool.write(
            cr, uid, self.patient_id, {'family_name': 'Wren',
                                       'patient_identifier': '1231231231'})
        self.patient_id2 = self.patient_ids[1]
        self.patient_id3 = self.patient_ids[2]

        spell_data = {
            'patient_id': self.patient_id,
            'pos_id': self.pos_id,
            'location_id': self.bed_id,
            'code': '1234',
            'start_date': dt.now().strftime(dtf)}
        spell2_data = {
            'patient_id': self.patient_id2,
            'pos_id': self.pos_id,
            'location_id': self.bed_id1,
            'code': 'abcd',
            'start_date': dt.now().strftime(dtf)}
        spell3_data = {
            'patient_id': self.patient_id3,
            'pos_id': self.pos_id,
            'location_id': self.bed_id2,
            'code': '5678',
            'start_date': dt.now().strftime(dtf)}

        spell_activity_id = self.spell_pool.create_activity(
            cr, uid, {}, spell_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.spell_id = spell_activity_id
        spell_activity_id = self.spell_pool.create_activity(
            cr, uid, {}, spell2_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.spell_id2 = spell_activity_id
        spell_activity_id = self.spell_pool.create_activity(
            cr, uid, {}, spell3_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.spell_id3 = spell_activity_id
        self.ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55
        }
        self.ews_data2 = {
            'respiration_rate': 59,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 44.9,
            'blood_pressure_systolic': 300,
            'blood_pressure_diastolic': 280,
            'pulse_rate': 250,
            'avpu_text': 'U'
        }

    def test_01_test_flag_set_on_spell(self):
        # get the spell registry and check that it has report_
        # printed key and it's False
        flag_present = 'report_printed' in self.spell_pool
        flag_value = self.spell_pool._defaults['report_printed']
        self.assertEqual(flag_present, True,
                         'Flag not set on Spell class properly')
        self.assertEqual(flag_value, False,
                         'Flag value not set correctly')

    def test_02_test_flag_set_on_location(self):
        # get the location registry and check that it has
        # report_printed key and it's False
        flag_present = 'backup_observations' in self.location_pool
        flag_value = self.location_pool._defaults['backup_observations']
        self.assertEqual(flag_present, True,
                         'Flag not set on location class properly')
        self.assertEqual(flag_value, False, 'Flag value not set correctly')

    def test_03_test_flag_changed_by_observation_complete(self):
        # get a spell and set flag to True
        cr, uid = self.cr, self.uid
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
        self.spell_pool.write(cr, uid, spell_id, {'report_printed': True})
        pre_complete_flag_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(pre_complete_flag_value, True,
                         'Flag not set correctly by write method')

        # complete an observation and check flag is now False
        ews_activity_id = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id},
            {'patient_id': self.patient_id})
        self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        self.ews_pool.complete(cr, uid, ews_activity_id)
        post_complete_flag_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(post_complete_flag_value, False,
                         'Flag not updated by complete method properly')

    def test_04_test_flag_changed_by_report_printing_method(self):
        # complete an observation and check flag is now False
        cr, uid = self.cr, self.uid
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
        ews_activity_id = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id},
            {'patient_id': self.patient_id})
        self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        self.ews_pool.complete(cr, uid, ews_activity_id)
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete method properly')

        # run the report printing method in api and check that the
        # flag is set to True
        self.api_pool.print_report(cr, uid, spell_id)
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, True,
                         'Flag not updated by printing method properly')

    def test_05_test_flag_changed_by_printing_method_no_spell_defined(self):
        # complete an observation and check flag is now False
        cr, uid = self.cr, self.uid
        # clean up before test
        dirty_spell_ids = self.spell_pool.search(
            cr, uid, [['report_printed', '=', False]])
        self.spell_pool.write(
            cr, uid, dirty_spell_ids, {'report_printed': True})

        # add demo data
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
        spell_id2 = self.spell_pool.get_by_patient_id(
            cr, uid, self.patient_id2)
        ews_activity_id = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id},
            {'patient_id': self.patient_id}
        )
        ews_activity_id2 = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id2},
            {'patient_id': self.patient_id2}
        )
        self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        self.ews_pool.complete(cr, uid, ews_activity_id)
        self.ews_pool.submit(cr, uid, ews_activity_id2, self.ews_data2)
        self.ews_pool.complete(cr, uid, ews_activity_id2)
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete method properly')
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id2, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete '
                         'method properly on second report')

        # run the report printing method in api and check
        # that the flag is set to True
        self.api_pool.print_report(cr, uid)
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, True,
                         'Flag not updated by printing method properly')
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id2, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, True,
                         'Flag not updated by printing method properly')

    def test_06_test_flag_not_change_by_wkhtmltopdf_error(self):
        # complete an observation and check flag is now False
        cr, uid = self.cr, self.uid

        def mock_print(*args, **kwargs):
            global mocked_print_called
            mocked_print_called += 1
            if mocked_print_called == 2:
                raise osv.except_osv(
                    'Report (PDF)',
                    'Wkhtmltopdf failed (error code: -11). Message:'
                )
            return mock_print.origin(*args, **kwargs)

        self.registry('report')._patch_method('_run_wkhtmltopdf', mock_print)
        # clean up before test
        dirty_spell_ids = self.spell_pool.search(
            cr, uid, [['report_printed', '=', False]])
        self.spell_pool.write(
            cr, uid, dirty_spell_ids, {'report_printed': True})

        # add demo data
        spell_id = self.spell_pool.get_by_patient_id(
            cr, uid, self.patient_id)
        spell_id2 = self.spell_pool.get_by_patient_id(
            cr, uid, self.patient_id2)
        spell_id3 = self.spell_pool.get_by_patient_id(
            cr, uid, self.patient_id3)
        ews_activity_id = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id},
            {'patient_id': self.patient_id}
        )
        ews_activity_id2 = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id2},
            {'patient_id': self.patient_id2}
        )
        ews_activity_id3 = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': self.spell_id3},
            {'patient_id': self.patient_id3}
        )
        self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        self.ews_pool.complete(cr, uid, ews_activity_id)
        self.ews_pool.submit(cr, uid, ews_activity_id2, self.ews_data2)
        self.ews_pool.complete(cr, uid, ews_activity_id2)
        self.ews_pool.submit(cr, uid, ews_activity_id3, self.ews_data2)
        self.ews_pool.complete(cr, uid, ews_activity_id3)

        # Test that all false
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete method properly')
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id2, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete method '
                         'properly on second report')
        pre_report_value = self.spell_pool.read(
            cr, uid, spell_id3, ['report_printed'])['report_printed']
        self.assertEqual(pre_report_value, False,
                         'Flag not updated by complete '
                         'method properly on second report')

        # run the report printing method in api and check that the flag
        # is set to True
        self.api_pool.print_report(cr, uid)
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, True,
                         'Flag not updated by printing method properly')
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id2, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, False,
                         'Flag not updated by printing method properly')
        post_report_value = self.spell_pool.read(
            cr, uid, spell_id3, ['report_printed'])['report_printed']
        self.assertEqual(post_report_value, True,
                         'Flag not updated by printing method properly')

        # Test that only failed spell is returned for printing
        new_dirty_spell_ids = self.spell_pool.search(
            cr, uid, [['report_printed', '=', False]])
        self.assertEqual(
            new_dirty_spell_ids, [spell_id2],
            'Spells returned post failed print not correct')

        self.registry('report')._revert_method('_run_wkhtmltopdf')

    def test_07_test_no_spell_domain_is_empty_when_no_non_printed_spells(self):
        cr, uid = self.cr, self.uid
        loc_ids = self.location_pool.search(
            cr, uid, [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True]
            ]
        )
        dirty_spell_ids = self.spell_pool.search(
            cr, uid, [
                ['report_printed', '=', False],
                ['state', 'not in', ['completed', 'cancelled']],
                ['location_id', 'child_of', loc_ids]
            ]
        )
        self.spell_pool.write(
            cr, uid, dirty_spell_ids, {'report_printed': True})

        test_empty = self.spell_pool.search(
            cr, uid, [
                ['report_printed', '=', False],
                ['state', 'not in', ['completed', 'cancelled']],
                ['location_id', 'child_of', loc_ids]
            ]
        )
        self.assertEqual(
            test_empty, [],
            'No Spell Domain returned spells when should be empty')

    def test_08_test_no_spell_domain_is_empty_when_no_non_printed_spells(self):
        cr, uid = self.cr, self.uid
        loc_ids = self.location_pool.search(
            cr, uid, [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True]
            ]
        )
        dirty_spell_ids = self.spell_pool.search(
            cr, uid, [
                ['report_printed', '=', False],
                ['state', 'not in', ['completed', 'cancelled']],
                ['location_id', 'child_of', loc_ids]
            ]
        )
        test_spell = dirty_spell_ids[0]
        self.spell_pool.write(
            cr, uid, dirty_spell_ids[1:], {'report_printed': True})

        test_empty = self.spell_pool.search(
            cr, uid, [
                ['report_printed', '=', False],
                ['state', 'not in', ['completed', 'cancelled']],
                ['location_id', 'child_of', loc_ids]
            ]
        )
        self.assertEqual(
            test_empty, [test_spell],
            'No Spell Domain returned more than one spell')

    def test_09_test_report_added_to_database(self):
        # run the report printing method in api and check that report
        #  added to DB
        cr, uid = self.cr, self.uid
        attachment_id = self.api_pool.add_report_to_database(
            cr, uid,
            'nh.clinical.observation_report',
            'test_data',
            'test_report.pdf',
            'nh.clinical.observation_report_wizard',
            1
        )

        attachment_data = self.ir_pool.read(
            cr, uid, attachment_id, ['datas'])[0]['datas']
        report_str = base64.decodestring(attachment_data)

        self.assertEqual(
            report_str, 'test_data', 'Report not added to database properly')

    def test_10_test_report_added_to_file_system(self):
        # run the report printing method in api and check that file
        # was created on FS
        # /bcp/out
        self.api_pool.add_report_to_backup_location('/bcp/out',
                                                    'test_data',
                                                    'test_report')
        with open('/bcp/out/test_report.pdf', 'r') as report_file:
            file_content = report_file.read()
        self.assertEqual(
            file_content,
            'test_data',
            'Report not added to filesystem properly'
        )

    def test_11_test_report_filename_is_correct(self):
        # run the report pringing method in teh api and
        # check that the file is correctly named
        # ward_surname_nhs_number
        cr, uid = self.cr, self.uid
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
        nhs_number = '1231231231'
        ward = None
        surname = 'Wren'
        file_name = '{w}_{s}_{n}'.format(w=ward, s=surname, n=nhs_number)

        # do print_report
        self.api_pool.print_report(cr, uid, spell_id)
        # check backup file name
        backup_exists = os.path.isfile('/bcp/out/{0}.pdf'.format(file_name))
        self.assertEqual(
            backup_exists, True, 'Report incorrectly named on file system')

    def test_12_test_general_settings_view_updated_with_options(self):
        # Grab the view XML and make sure it has the overridden values
        cr, uid = self.cr, self.uid
        view_pool = self.registry('ir.ui.view')
        parent_view_id = view_pool.search(
            cr, uid, [
                ['model', '=', 'base.config.settings'],
                ['mode', '=', 'primary']
            ]
        )[0]
        child_view_ids = view_pool.read(
            cr, uid,
            parent_view_id,
            ['inherit_children_ids']
        )['inherit_children_ids']
        our_view_id = view_pool.search(
            cr, uid, [['name', '=', 'base.config.settings.nhclinical']])[0]
        self.assertTrue(
            our_view_id in child_view_ids,
            'View not in list of inherited views for general settings screen')

    def test_13_test_gen_settings_loads_backup_enabld_wards_correctly(self):
        # Using the demo ward call the function to load the data
        cr, uid = self.cr, self.uid
        settings_pool = self.registry('base.config.settings')
        get_vals = settings_pool.get_default_all(cr, uid, [])
        self.assertEqual(
            get_vals['locations_to_print'][0],
            self.wu_id,
            'Ward U id not in location to print from settings')

    def test_14_gen_settings_set_location_removes_all_wards_not_defined(self):
        cr, uid = self.cr, self.uid
        settings_pool = self.registry('base.config.settings')
        record = settings_pool.create(cr, uid, {'locations_to_print': []})
        settings_pool.set_locations(cr, uid, [record])
        get_vals = settings_pool.get_default_all(cr, uid, [])
        self.assertEqual(
            get_vals['locations_to_print'],
            [], 'Ward U not removed from backed up wards')
