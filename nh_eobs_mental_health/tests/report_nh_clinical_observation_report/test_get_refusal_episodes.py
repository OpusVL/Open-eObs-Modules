from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestGetRefusalEpisodes(TransactionCase):
    """
    Test the method that collects the refusal episodes for the spell
    """

    def setUp(self):
        super(TestGetRefusalEpisodes, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.get_open_obs()
        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.refused_obs = clinical_risk_sample_data.REFUSED_DATA
        self.partial_obs = clinical_risk_sample_data.PARTIAL_DATA_ASLEEP
        self.full_obs = clinical_risk_sample_data.MEDIUM_RISK_DATA

    def test_no_refusals(self):
        """
        Test that on finding no refusals the method returns an empty array
        """
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertFalse(values)

    def test_refused(self):
        """
        Test that having a refusal returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)

    def test_refused_then_full(self):
        """
        Test that having a refusal then a full observation returns a count of
        1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.full_obs)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)

    def test_refused_then_partial(self):
        """
        Test that having a refusal then a partial observation returns a
        count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.partial_obs)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)

    def test_refused_then_refused(self):
        """
        Test that having a refusal then another refusal returns a count of
        2
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 2)

    def test_refused_then_pme(self):
        """
        Test that having a refusal then a patient monitoring exception
        returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.start_pme()
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)

    def test_refused_then_pme_and_refused_after_restart(self):
        """
        Test that having a refusal then a patient monitoring exception
        returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.start_pme()
        self.test_utils_model.end_pme()
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0].get('count'), 1)
        self.assertEqual(values[1].get('count'), 1)

    def test_refused_then_transfer(self):
        """
        Test that having a refusal then a transfer returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.transfer_patient('WB')
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)

    def test_refused_then_discharge(self):
        """
        Test that having a refusal then a discharge returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.discharge_patient()
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
