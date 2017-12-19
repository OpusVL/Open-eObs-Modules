# coding: utf-8
import time
from datetime import datetime, timedelta

from \
    openerp.addons.nh_eobs_slam.tests.nh_clinical_patient_observation_ews \
    import test_initial_obs_freq_change
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

date_start = None

initialobscommon = test_initial_obs_freq_change.InitialObsFreqCommon


class TestInitialEWSRaceCondition(initialobscommon):

        def setUp(self):
            super(TestInitialEWSRaceCondition, self).setUp()
            self.ews_pool = self.registry(
                'nh.clinical.patient.observation.ews')

        def tearDown(self):
            self.spell_pool._revert_method('read')
            self.ews_pool._revert_method('change_activity_frequency')
            super(TestInitialEWSRaceCondition, self).tearDown()

        def test_one_second_before(self):
            def mock_spell_read(*args, **kwargs):
                if 'date_start' in globals() and date_start:
                    date_started = [arg for arg in args
                                    if arg == ['date_started']]
                    if date_started:
                        td = timedelta(hours=95, minutes=59, seconds=59)
                        four_days_ago = date_start - td
                        return {'date_started': four_days_ago.strftime(dtf)}
                return mock_spell_read.origin(*args, **kwargs)

            def mock_ews_change_activity_freq(*args, **kwargs):
                global date_start
                date_start = datetime.now()
                time.sleep(1)
                return mock_ews_change_activity_freq.origin(*args, **kwargs)

            # Mocks read of last obs terminated date too, all reads in fact.
            self.spell_pool._patch_method('read', mock_spell_read)
            self.ews_pool._patch_method('change_activity_frequency',
                                        mock_ews_change_activity_freq)
            self.assertEqual(
                self.complete_obs(clinical_risk_sample_data.NO_RISK_DATA), 720,
                msg='Did not pass race condition due to complete method pause')

        def test_one_second_after(self):
            def mock_spell_read(*args, **kwargs):
                if 'date_start' in globals() and date_start:
                    if args[4] == ['date_started']:
                        td = timedelta(hours=96, minutes=00, seconds=01)
                        four_days_ago = date_start - td
                        return {'date_started': four_days_ago.strftime(dtf)}
                return mock_spell_read.origin(*args, **kwargs)

            def mock_ews_change_activity_freq(*args, **kwargs):
                global date_start
                date_start = datetime.now()
                time.sleep(1)
                return mock_ews_change_activity_freq.origin(*args, **kwargs)

            self.spell_pool._patch_method('read', mock_spell_read)
            self.ews_pool._patch_method('change_activity_frequency',
                                        mock_ews_change_activity_freq)
            self.assertEqual(
                self.complete_obs(clinical_risk_sample_data.NO_RISK_DATA),
                1440,
                msg='Did not pass race condition due to complete method pause')
